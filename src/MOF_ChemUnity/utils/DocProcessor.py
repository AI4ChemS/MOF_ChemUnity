from typing import List, Optional
from copy import deepcopy


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
        return text[:min_index].strip()  # remove any trailing spaces
    
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
    ) -> List[Document] | str:
        
        '''
        The process function prepares the input file for vectore storage. 
        This includes loading the file based off its location, and initially splitting the text using "load_and_split".
        This will use a RecursiveCharacterTextSplitter to split a file up based off of its section headers.
        Following this, irrelevant text is filtered out based off given "headers" that are irrelevant.
        Lastly, the text is furhter split down using the CharacterTextSplitter.
        '''

        # Check file extension, assign appropriate loader, load and split text
        extension = file_name.split(".")[-1].lower()
        if extension == "pdf":
            self.loader = PDFPlumberLoader(file_path=file_name, extract_images=False)

        elif extension == "md":
            self.loader = UnstructuredMarkdownLoader(file_path = file_name)
                        
        else:
            print("file is not supported")
            raise AssertionError()
        
        self.pages = self.loader.load_and_split()
        
        # Filter documents using the provided "headers" as filter words
        try:
            # Attempt to filter the documents
            sliced_pages = self.filter_documents(self.pages, self.headers)
            
            # Check if the entire page_content got filtered out - this will be the case if a filter word like "references" appears first in the document
            if not sliced_pages[0].page_content.strip():
                print("Filtering out irrelvant sections resulted in empty page_content. Unfiltered pages will be used instead.")
                sliced_pages = self.pages
        except Exception as e:
            # Handle potential exceptions from the filter_documents method
            print(f"An error occurred while filtering documents: {e}")
            sliced_pages = self.pages  # Fall back to original pages in case of an exception

        # If a chunk size is provided, split the documents up further
        text_splitter = CharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        ) 

        sliced_pages = text_splitter.split_documents(sliced_pages)

        return sliced_pages













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
