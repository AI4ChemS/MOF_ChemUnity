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
            "abstract",
            "introduction\n",
            "references\n",
            "acknowledgements\n",
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

        match_indices = [
            0,
        ]
        for header in headers if headers else self.headers:
            match_indices.append(
                text.lower().find(
                    header,
                    max(match_indices),
                )
            )

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

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size if chunk_size else self.chunk_size,
                chunk_overlap=chunk_overlap if chunk_overlap else self.chunk_overlap,
            )

            ret_docs = []
            for i in doc:
                ret_docs.extend(splitter.create_documents([i.page_content]))
            return ret_docs
        else:
            return "File format is not support"
