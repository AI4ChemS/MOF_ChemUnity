from src.MOF_ChemUnity.utils.DataModels import MOFRefCode, MOFRefCodeList, RefCodeJustification
from MOF_ChemUnity.Matching_Prompts import MATCH_REFCODES, CHECK_JUSTIFICATION, RECHECK, MATCH_REFCODES_SHORT, CHECK_JUSTIFICATION_SHORT
from utils.DocProcessor import DocProcessor
import BaseAgent

from os import path
from typing import List, Optional
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.vectorstores import FAISS



class MatchingAgent(BaseAgent):
    """
    MatchingAgent extends BaseAgent to be applied to MOF reference code matching
    """
    
    def __init__(self, 
                llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.3),
                embeddings=OpenAIEmbeddings(model="text-embedding-ada-002"),
                parser_llm=None,
                structured_llm=True,
                processor=None):
        # Initialize BaseAgent instance
        super().__init__(llm, embeddings, parser_llm, structured_llm, processor)

    
    # This function is used to format the csd data in a clearer way - this is used before the info is sent into the prompt
    def pretty_csd_data(self) -> str:
        result = ""
        for key, value in self.csd_data.items():
            result += f'-CSD Reference Code: {key}:'
            result += value.__str__().replace('{', '[').replace('}',']')
            result += '\n'
        return result

    # This is the main function of the class, generating the matching agent response
    def agent_response(self, csd_data, paper_file, read_prompt=MATCH_REFCODES, vector_store=None, ret_docs = False, store_vs = True):
        # Set up vector store
        if vector_store:
            vs = FAISS.load_local(vector_store, OpenAIEmbeddings(model = 'text-embedding-ada-002'))
        else:
            vs = self.create_vector_store(paper_file, store_vs=store_vs)   
        
        # Define Parsers
        single_parser = self.Parse_Output(MOFRefCode)

        parser = self.Parse_Output(MOFRefCodeList)

        bool_parser = self.Parse_Output(RefCodeJustification)

        # Begin Process
        print("-"*14+f"{paper_file.split('/')[-1]}"+"-"*14)
        print("Action: read_doc")

        # Step 1: Reading the document
        (answer1, docs) = self.RAG_Chain_Output(prompt = read_prompt.format(self.pretty_csd_data()))

        print("\nResult: ")
        print(answer1["result"])

        # Step 2: Parse Output using Pydantic
        list_mofs = parser.invoke(f"Parse the following text into the structured output\nText:\n{answer1['result']}")

        print("\nParsed Result:")
        for mof in list_mofs.mofs:
            print(mof)

        return (list_mofs, docs) if ret_docs else list_mofs



