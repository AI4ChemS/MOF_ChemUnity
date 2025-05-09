import pickle
import os
from typing import List, Optional

from openai import RateLimitError
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough

from MOF_ChemUnity.utils.DocProcessor import DocProcessor

QA_PROMPT = (
    "Answer the user question using the information provided in the documents."
    "Don't make up answer!\n"
    "Documents:\n{context}\n\n Question:\n{input}"
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
        processor: Optional[DocProcessor] = None,
    ):
        self.llm = llm if llm else ChatOpenAI(model="gpt-4o", temperature=0)
        self.embeddings = embeddings if embeddings else OpenAIEmbeddings(model="text-embedding-ada-002")
        self.parser = parser_llm if parser_llm else self.llm
        self.structured_llm = structured_llm
        self.processor = processor if processor else DocProcessor()
        pass

    def create_vector_store(
        self,
        doc_path: str,
        processor: Optional[DocProcessor] = None,
        store_vs=False,
        store_folder: Optional[str] = None,
    ):
        if processor:
            pages = processor.process(doc_path)
        else:
            pages = self.processor.process(doc_path)

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
        pydantic_output: Optional[BaseModel] = None
    ):
        result = self._RetrievalQAChain(
            prompt,
            vectorstore,
            k=k,
            min_k=min_k,
            search_type="similarity",
            fetch_k=50,
            memory=None,
            pydantic_output=pydantic_output
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
        search_type="similarity",
        pydantic_output: Optional[BaseModel] = None,
        memory=None,
    ):
        while k >= min_k:
            try:
                retriever = vectorstore.as_retriever(
                    search_type=search_type, search_kwargs={"k": k, "fetch_k": fetch_k}
                )

                qa_chat_prompt = ChatPromptTemplate.from_template(QA_PROMPT)

                if pydantic_output:
                    llm = self.Parse_Output(pydantic_output)
                    qa_chain = (
                    {
                        "context": retriever | format_docs,
                        "input": RunnablePassthrough(),
                    }
                    | qa_chat_prompt 
                    | llm)
                    result = qa_chain.invoke(prompt)
                else:
                    llm = self.llm

                    docs_chain = create_stuff_documents_chain(llm, qa_chat_prompt)
                    qa_chain = create_retrieval_chain(retriever, docs_chain)

                    result = qa_chain.invoke({"input": prompt})

                return (result, retriever.invoke(prompt))

            except RateLimitError as e:
                print(e)
                print(
                    "hitting the context window limit. Adjusting k to try again... \n"
                )
                k -= 1

        print("failed to retriever results after multiple attempts")
        return None

    def get_prompt_for_task(self) -> ChatPromptTemplate:
        pass
