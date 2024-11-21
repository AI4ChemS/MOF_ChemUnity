import pickle
import os
from typing import List, Optional

from pydantic import BaseModel, Field
from langchain.chains import RetrievalQA


from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.MOF_ChemUnity.utils.DocProcessor import LoadDoc

QA_PROMPT = (
    "Answer the user question using the information provided in the documents."
    "Don't make up answer!\n"
    "Question:\n{input}\n\n Documents:\n{context}"
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


class BaseAgent:
    def __init__(
        self,
        llm = None,
        embeddings= None,
        parser_llm=None,
        structured_llm: bool = True,
        processor: Optional[LoadDoc] = None,
    ):
        self.llm = llm if llm else ChatOpenAI(model="gpt-4o", temperature=0)
        self.embeddings = embeddings if embeddings else OpenAIEmbeddings(model="text-embedding-ada-002")
        self.parser = parser_llm if parser_llm else self.llm
        self.structured_llm = structured_llm

        self.processor = processor 
        pass

    def create_vector_store(
        self,
        doc_path: str,
        processor: Optional[LoadDoc] = None,
        store_vs=False,
        store_folder: Optional[str] = None,
    ):

        processor = LoadDoc(file_name=doc_path, encoding="utf8")
        pages = processor.process(['references ', 'acknowledgement', 'acknowledgments', 'references\n'],
                                             chunk_size=8000, chunk_overlap=1000, chunking_type="fixed-size")

        faiss_index = FAISS.from_documents(pages, self.embeddings)

        if not store_vs:
            return faiss_index

        # Generate the storage folder path
        file_name = os.path.basename(doc_path).rsplit(".", 1)[0]
        if not store_folder:
            dirn = os.path.dirname(doc_path).rsplit("/", 1)[0]
            store_folder = os.path.join(dirn, "vs", file_name)

        # Ensure the folder exists
        if not os.path.exists(store_folder):
            os.makedirs(store_folder)

        # Save the vector store
        faiss_index.save_local(store_folder)

        print(
            f"Saved vector store for {doc_path} in {store_folder}"
        )

        return faiss_index

    def RAG_Chain_Output(
        self,
        prompt: str,
        vectorstore: FAISS,
        k: int = 9,
        min_k: int = 2,
    ):
        result = self._RetrievalQAChain(
            prompt,
            vectorstore,
            k=k,
            min_k=min_k,
            search_type="mmr",
            fetch_k=50,
            memory=None,
        )

        return result

    def Parse_Output(self, pydantic_object: BaseModel):
        if self.structured_llm:
            return self.parser.with_structured_output(pydantic_object)
        else:
            parser = PydanticOutputParser(pydantic_object=pydantic_object)

            formatting_prompt = "You need to parse the user inputted text to fill the specified JSON output schema - only return the JSON output: \
\nOutput_schema:\n{instructions}\nUser Text:\n{text}"

            formatting_prompt = ChatPromptTemplate.from_template(formatting_prompt)
            formatting_prompt = formatting_prompt.partial(
                instructions=parser.get_format_instructions()
            )

            parsing_chain = (
                {"text": RunnablePassthrough()}
                | formatting_prompt
                | self.parser
                | parser
            )
            return parsing_chain

    def _RetrievalQAChain(
        self,
        prompt: str,
        vectorstore,
        k,
        min_k,
        fetch_k: int,
        search_type="mmr",
        memory=None,
    ):
        while k >= min_k:
            try:
                retriever = vectorstore.as_retriever(
                    search_type=search_type, search_kwargs={"k": k, "fetch_k": fetch_k}
                )

                qa_chat_prompt = ChatPromptTemplate.from_template(QA_PROMPT)

                docs_chain = create_stuff_documents_chain(self.llm, qa_chat_prompt)
                qa_chain = create_retrieval_chain(retriever, docs_chain)

                result = qa_chain.invoke({"input": prompt})

                qa_prompt = "Answer the user question using the information provided in the documents. Don't make up answer!\n \
Question:\n {question}\n\n Documents:\n {context}"

                qa_prompt = ChatPromptTemplate.from_template(qa_prompt)

                qa_chain = RetrievalQA.from_chain_type(llm=self.llm, retriever=retriever, memory=memory, chain_type="stuff")

                result = qa_chain.invoke(prompt)
                return (result, retriever.invoke(prompt))

            except Exception as e:
                print(e)
                print(
                    "hitting the context window limit. Adjusting k to try again... \n"
                )
                k -= 1

        print("failed to retriever results after multiple attempts")
        return None

    def get_prompt_for_task(self) -> ChatPromptTemplate:
        pass
