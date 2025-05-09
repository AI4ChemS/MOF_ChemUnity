import requests
import openai
import numpy as np
import pandas as pd
import faiss
import time  
import os
import urllib

class CrossDocUtil:
    def __init__(self, SCOPUS_API_KEY):
        self.SCOPUS_API_KEY = SCOPUS_API_KEY
    
    def search_scopus(self, mof_name, count = 50, batch_size = 100, wait_time = 1, abstract_wait = 1):
        """
        Searches Scopus for articles related to the given MOF name and synthesis,
        retrieves metadata (Title, DOI), and fetches full abstracts.

        Parameters:
            mof_name (str): The name of the MOF to search for.
            count (int): The total number of papers to retrieve (default=50).
            batch_size (int): Max papers per request (Scopus limit = 200, using 100 for better control).
            wait_time (float): Delay (seconds) between Scopus search requests to avoid rate limits.
            abstract_wait (float): Delay (seconds) between abstract retrieval requests.

        Returns:
            pd.DataFrame: A DataFrame containing retrieved papers (Title, Abstract, DOI).
        """
        search_url = "https://api.elsevier.com/content/search/scopus"
        abstract_url_base = "https://api.elsevier.com/content/abstract/doi/"
        headers = {"X-ELS-APIKey": self.SCOPUS_API_KEY, "Accept": "application/json"}

        papers = []
        retrieved = 0  # Track total retrieved papers

        while retrieved < count:
            remaining = count - retrieved
            current_batch_size = min(batch_size, remaining)  # Ensure we don’t exceed count
            
            params = {
                "query": f'TITLE-ABS-KEY("{mof_name}" AND synthesis) AND DOCTYPE(ar)',
                "count": current_batch_size,
                "start": retrieved
            }

            time.sleep(wait_time)  # Prevent hitting rate limits
            response = requests.get(search_url, headers=headers, params=params)

            if response.status_code != 200:
                print(f"Error: Received status code {response.status_code}")
                break  # Stop if error

            data = response.json()

            if "search-results" in data and "entry" in data["search-results"]:
                for entry in data["search-results"]["entry"]:
                    title = entry.get("dc:title", "")
                    doi = entry.get("prism:doi", "N/A")
                    abstract = entry.get("dc:description", "") or "No abstract available"

                    # Retrieve full abstract if missing
                    if abstract == "No abstract available" and doi != "N/A":
                        time.sleep(abstract_wait)  # Prevent rate limits
                        abstract_url = f"{abstract_url_base}{doi}"
                        abstract_response = requests.get(abstract_url, headers=headers)
                        
                        if abstract_response.status_code == 200:
                            abstract_data = abstract_response.json()
                            abstract = abstract_data.get("abstracts-retrieval-response", {}).get("coredata", {}).get("dc:description", "No abstract available")

                    papers.append({"title": title, "abstract": abstract, "doi": doi})
                    retrieved += 1

                    if retrieved >= count:
                        break  # Stop when we reach `count` papers

                if len(data["search-results"]["entry"]) < current_batch_size:
                    break  # Stop if no more papers left in Scopus

            else:
                print("No results found or incorrect response format")
                break

        # Convert to DataFrame
        papers_df = pd.DataFrame(papers, columns=["title", "abstract", "doi"])

        if len(papers_df) < count:
            print(f"Warning: Could not find {count} papers. Returning {len(papers_df)} instead.")

        return papers_df
    
    def vector_search(self, query_text, index, abstracts, top_k = 5):
        query_embedding = np.array(self.get_embedding(query_text)).reshape(1, -1)
        _, top_indices = index.search(query_embedding, top_k)
        return [(abstracts[i], i) for i in top_indices[0]]
    
    def get_embedding(self, text, model = "text-embedding-ada-002"):
        if not text.strip():  # Handle empty abstracts
            return np.zeros(1536)  # Default embedding size for OpenAI models
        response = openai.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    
    def download_full_texts(self, df, save_path = "full_text_xml", wait_time = 1.0):
        """
        Downloads full-text XML files for papers in a DataFrame using Elsevier's Full-Text Retrieval API.

        Parameters:
            df (pd.DataFrame): DataFrame containing a "DOI" column.
            save_path (str): Directory to save the XML files (default: "full_text_xml").
            wait_time (float): Delay (seconds) between API requests to avoid rate limits.

        Returns:
            dict: Summary of download results (success, not_found, error counts)
        """
        # Ensure the save directory exists
        os.makedirs(save_path, exist_ok=True)
        
        base_url = "https://api.elsevier.com/content/article/doi/{doi}?view=FULL"
        headers = {
            "X-ELS-APIKey": "345cae7ca89972e7e1c24375fe6b1f49",  # Your Elsevier API key
            "Accept": "text/xml"
        }
        
        results = {"success": 0, "not_found": 0, "error": 0}

        for idx, row in df.iterrows():
            # Check if "doi" or "DOI" is in the DataFrame
            doi_col = next((col for col in ["doi", "DOI"] if col in row.index), None)
            
            if doi_col is None:
                print("No DOI column found in DataFrame. Please ensure it exists as 'doi' or 'DOI'.")
                return results
                
            doi = row.get(doi_col)

            if not isinstance(doi, str) or doi.strip() == "":
                print(f"Skipping invalid DOI at index {idx}")
                continue
            
            # URL encode the DOI
            encoded_doi = urllib.parse.quote(doi, safe='')
            xml_filename = os.path.join(save_path, f"{doi.replace('/', '_')}.xml")
            
            # Skip if file already exists
            if os.path.exists(xml_filename):
                print(f"File already exists, skipping: {xml_filename}")
                results["success"] += 1
                continue

            # Introduce a delay to avoid rate limiting
            time.sleep(wait_time)

            try:
                url = base_url.format(doi=encoded_doi)
                print(f"Requesting: {url}")
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    with open(xml_filename, "wb") as xml_file:
                        xml_file.write(response.content)
                    print(f"Downloaded: {xml_filename}")
                    results["success"] += 1
                elif response.status_code == 404:
                    print(f"DOI not found: {doi} (Status: 404)")
                    results["not_found"] += 1
                else:
                    print(f"Failed to download {doi}: Status {response.status_code}")
                    print(f"Response content: {response.text[:200]}...")  # Print first 200 chars of response
                    results["error"] += 1

            except requests.RequestException as e:
                print(f"Error downloading {doi}: {e}")
                results["error"] += 1
        
        print(f"\nSummary: {results['success']} successful, {results['not_found']} not found, {results['error']} errors")
        return results