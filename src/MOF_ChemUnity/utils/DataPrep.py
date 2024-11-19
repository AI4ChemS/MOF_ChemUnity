import pandas as pd
import os
"""
THree instance variables must be declared for this class:
1 - doi_folder_path: The path to the folder containing all of the .pdf, .xml, you wish to process
2 - csd_info_path: The path to the .csv file containing ALL info extracted from CSD Python API - we extracted info for all papers contained within CoRE + QMOF
3 - feature_list: The list of features (columns) found within the CSD .csv file that will be used in the matching prompt
"""
class Data_Prep:

    def __init__(self, paper_folder_path, csd_info_path, feature_list): 
        self.paper_folder_path = paper_folder_path
        self.csd_info_path = csd_info_path
        self.feature_list = feature_list
        self.DOI_list = None  

    '''
    The purpose of this method is to organize every DOI that you wish to use for text mining
    The end result will be a pandas dataframe containing DOI, File Name, Publisher, and File Format
    '''

    def gather_doi_info(self):
        file_data = []

        # Walk through the directory and its subdirectories
        for root, dirs, files in os.walk(self.paper_folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                # Check if the file is either .md or .xml
                if file_name.endswith('.md') or file_name.endswith('.xml'):
                    # Extract DOI by replacing underscores with "/"
                    doi = file_name.rsplit('.', 1)[0].replace('_', '/')
                    
                    # Extract file format from the file extension
                    file_format = file_name.rsplit('.', 1)[-1]
                    
                    # Append the data to the list
                    file_data.append({
                        "DOI": doi,
                        "File Name": file_name,
                        "File Format": file_format,
                        "File Path": file_path,
                    })

        # Convert the list to a DataFrame
        doi_info_df = pd.DataFrame(file_data)
        self.DOI_list = doi_info_df['DOI']  # Set DOIs as an instance variable here
        
        return doi_info_df


    
    '''
    The purpose of this method is to gather all CSD Python API data for every DOI you wish to use for text mining
    The end result will be a pandas dataframe containing all features you want to use in your matching prompt
    '''
    def gather_CSD_info(self):
        # Convert master csv into df
        master_df = pd.read_csv(self.csd_info_path)

        # Strip white spaces from strings in case an error exists
        master_df["DOI"] = master_df["DOI"].str.strip()
        self.DOI_list = self.DOI_list.str.strip()

        # Filter out DOI_list not included in DOI_list
        filtered_df = master_df[master_df["DOI"].isin(self.DOI_list)]
            
        # Find and print DOI in DOI_list that weren't found in master_df
        missing_DOIs = set(self.DOI_list) - set(master_df["DOI"])
        if missing_DOIs:
            print(f"\nWARNING: {len(missing_DOIs)} DOIs not found in Master CSV:")
            print(f"Missing DOIs: {missing_DOIs}\n")


        # Filter out properties not included in column_list (always add journal info)
        columns_to_keep = ["Journal"] + [col for col in self.feature_list if col in filtered_df.columns]
        filtered_df = filtered_df[columns_to_keep]

        #Put Journal column first
        filtered_df = filtered_df[["Journal"] + [col for col in filtered_df.columns if col != "Journal"]]

        # Warn about missing columns
        missing_columns = set(self.feature_list) - set(filtered_df.columns)
        if missing_columns:
            print(f"\nWARNING: The following columns are not in the filtered DataFrame:")
            print(f"Missing Columns: {missing_columns}\n")

        return filtered_df
    
    
    '''
    This method executes gather_doi_info() and gather_csd_info() and compiles all information into one dataframe
    '''
    def gather_info(self):
        doi_info_df = self.gather_doi_info()
    
        csd_info_df = self.gather_CSD_info()

        # Merge all information into one dataframe, containing all relevant info for every DOI we wish to process - note, DOIs that are not found within the CSD info .csv file are filtered out here, due to the inner join
        publication_data_df = pd.merge(doi_info_df, csd_info_df, on='DOI', how='inner')
        return publication_data_df
    

