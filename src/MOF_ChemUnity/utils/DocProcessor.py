from typing import List, Optional

from langchain.schema import Document
from langchain.document_loaders.base import BaseLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
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
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
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

    def split_text(self, doc: Document, headers: List[str] = None) -> List[Document]:
        if not self.headers and not headers:
            return [doc]

        text = doc.page_content

        match_indices = [0,]
        for header in headers if headers else self.headers:
            header_match_index = text.lower().find(header,max(match_indices))
            if header_match_index > 0:
                match_indices.append(header_match_index)

        match_indices.append(len(text))
        match_indices.sort(reverse=False)

        return [
            Document(page_content=text[match_indices[i] : match_indices[i + 1]])
            for i in range(len(match_indices) - 1)
        ]

    def process(
        self,
        file_name: str,
        headers: Optional[List[str]] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> List[Document] | str:

        extension = file_name.split(".")[-1].lower()

        if extension == "pdf":
            loader = PDFPlumberLoader(file_path=file_name, extract_images=False)

            doc = loader.load()
            doc = self.split_text(doc, headers=headers)

        elif extension == "md":
            loader = UnstructuredMarkdownLoader(file_path = file_name, mode="fast", strategy="fast")
            
            doc = loader.load()
            doc = self.split_text(doc, headers=headers)

        else:
            print("file is not supported")
            raise AssertionError()

        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size if chunk_size else self.chunk_size,
                                          chunk_overlap=chunk_overlap if chunk_overlap else self.chunk_overlap) 
        ret_docs = []
        ret_docs.extend(splitter.create_documents([doc[1].page_content]))
        return ret_docs
