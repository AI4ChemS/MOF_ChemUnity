from typing import List, Optional
from copy import deepcopy
import os
import sys


from langchain.schema import Document
from langchain.document_loaders.base import BaseLoader

from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import (
    PDFPlumberLoader,
    UnstructuredMarkdownLoader,
    UnstructuredXMLLoader,
    UnstructuredHTMLLoader,
    TextLoader,
)

import xml.etree.ElementTree as ET
from MOF_ChemUnity.utils.XML_to_MD import TEI_Parser
from MOF_ChemUnity.utils.XML_to_MD import Elsevier_Parser

class DocProcessor:
    def __init__(
        self,
        chunk_size: int = 8000,
        chunk_overlap: int = 1000,
        headers: List[str] = [
            "acknowledgement",
            "references\n",
            "acknowledgements",
        ],
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.headers = headers
        pass

    # Used in filter_documents
    @staticmethod
    def find_in_document(document: Document, search_strings: List[str]) -> bool:
        """
        Searches for the given strings in the document content.

        Parameters:
        document : Document
            Document in which to search.
        search_strings : List[str]
            List of strings to search for.

        Returns:
        bool
            True if any of the search strings are found, False otherwise.
        """
        return any(
            search_string.lower() in document.page_content.lower()
            for search_string in search_strings
        )
    
    # Used in filter_documents
    @staticmethod
    def cut_text(text: str, keywords: List[str]) -> str:
        """
        Cuts the given text up to the first found keyword.

        Parameters:
        text : str
            The text to be cut.
        keywords : List[str]
            List of keywords to find in the text.

        Returns:
        str
            The cut text.
        """
        lower_text = text.lower()
        indices = [
            lower_text.find(keyword)
            for keyword in keywords
            if lower_text.find(keyword) != -1
        ]
        min_index = min(indices)
        return text[:min_index].strip()  # remove any trailing spacesself.loader = 
    
    def filter_documents(
        self, documents: List[Document], search_strings: List[str]
    ) -> List[Document]:
        """
        Filters documents based on the presence of search strings.
        use this if you wish to remove "Acknowledgments or "References"
        in a long research article.

        Parameters:
        documents : List[Document]
            List of documents to filter.
        search_strings : List[str]
            List of strings to search for.

        Returns:
        List[Document]
            List of filtered documents.
        """
        filtered_documents = deepcopy(documents)  # Create a deep copy of documents
        for i, doc in enumerate(filtered_documents):
            if self.find_in_document(doc, search_strings):
                filtered_documents[i].page_content = self.cut_text(
                    filtered_documents[i].page_content,
                    keywords=search_strings,
                )
                filtered_documents = filtered_documents[: i + 1]
                break
        return filtered_documents

    def process(
        self,
        file_name: str,
    ) -> tuple[List[Document], str]:
        extension = file_name.split(".")[-1].lower()
        
        # --- PDF ---
        if extension == "pdf":
            self.loader = PDFPlumberLoader(file_path=file_name, extract_images=False)
            vs_id = os.path.splitext(os.path.basename(file_name))[0]

        # --- Markdown ---
        elif extension == "md":
            self.loader = UnstructuredMarkdownLoader(file_path=file_name)
            vs_id = os.path.splitext(os.path.basename(file_name))[0]

        # --- XML ---
        elif extension == "xml":
            if "/XML/" not in file_name:
                print("Error: The input file is not located in a parent folder named 'XML'.")
                sys.exit(1)

            output_subdir = os.path.join(os.path.dirname(file_name), "Parsed_XML")
            os.makedirs(output_subdir, exist_ok=True)

            try:
                tree = ET.parse(file_name)
                root = tree.getroot()

                namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}
                idno_tag = root.find(".//tei:idno[@type='doi']", namespaces)

                if idno_tag is not None:
                    print(f"Detected TEI XML format in '{file_name}'")
                    import re
                    doi = idno_tag.text.strip()
                    doi_clean = re.sub(r'[^\w\-_.]', '_', doi)
                    md_file_location = os.path.join(output_subdir, f"{doi_clean}.md")
                    vs_id = doi_clean  # ✅ use this for vector store
                    xml_processor = TEI_Parser()
                    xml_processor.xml_to_markdown(file_name, md_file_location)
                    print(f"Converted '{file_name}' to Markdown at '{md_file_location}'")

                else:
                    namespaces.update({'xocs': 'http://www.elsevier.com/xml/xocs/dtd'})
                    xocs_doi_tag = root.find(".//xocs:doi", namespaces)
                    if xocs_doi_tag is not None:
                        print(f"Detected Elsevier XML format in '{file_name}'")
                        md_file_location = os.path.join(
                            output_subdir,
                            os.path.basename(file_name).replace(".xml", ".md")
                        )
                        vs_id = os.path.splitext(os.path.basename(file_name))[0]  # fallback
                        xml_processor = Elsevier_Parser()
                        xml_processor.xml_to_markdown(file_name, md_file_location)
                        print(f"Converted '{file_name}' to Markdown at '{md_file_location}'")
                    else:
                        print(f"Error: No recognized DOI tag found in '{file_name}'")
                        sys.exit(1)

            except Exception as e:
                print(f"Error processing the XML file '{file_name}': {e}")
                sys.exit(1)

            self.loader = UnstructuredMarkdownLoader(file_path=md_file_location)

        # --- Unsupported extension ---
        else:
            print("file is not supported")
            raise AssertionError()

        self.pages = self.loader.load_and_split()

        try:
            sliced_pages = self.filter_documents(self.pages, self.headers)
            if not sliced_pages[0].page_content.strip():
                print("Filtering removed all content. Reverting to unfiltered.")
                sliced_pages = self.pages
        except Exception as e:
            print(f"Filter error: {e}")
            sliced_pages = self.pages

        text_splitter = CharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        sliced_pages = text_splitter.split_documents(sliced_pages)

        return sliced_pages, vs_id  # ✅ return both













"""        extension = file_name.split(".")[-1].lower()

        if extension == "pdf":
            loader = PDFPlumberLoader(file_path=file_name, extract_images=False)

            doc = loader.load()
            doc = self.split_text(doc, headers=headers)

        elif extension == "md":
            loader = UnstructuredMarkdownLoader(file_path = file_name)
            
            doc = loader.load()
            doc = self.split_text(doc[0], headers=headers)

        else:
            print("file is not supported")
            raise AssertionError()

        splitter = CharacterTextSplitter(chunk_size=chunk_size if chunk_size else self.chunk_size,
                                          chunk_overlap=chunk_overlap if chunk_overlap else self.chunk_overlap) 
        ret_docs = []
        ret_docs.extend(splitter.create_documents([doc[0].page_content]))
        return ret_docs"""
