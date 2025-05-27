from genericpath import isfile
from os import path
from typing import Dict, List, Optional
from pydantic import BaseModel
from thefuzz import fuzz

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from MOF_ChemUnity.Agents.BaseAgent import BaseAgent
from MOF_ChemUnity.utils.DocProcessor import DocProcessor
from MOF_ChemUnity.utils.DataModels import Property, Verification, PropertyList

class ExtractionAgent(BaseAgent):
    def __init__(
            self,
            llm=None,
            embeddings=None,
            parser_llm=None,
            structured_llm: bool = True,
            processor: Optional[DocProcessor] = None,
            properties: Optional[List[str]] = None):

        self.llm = llm if llm else ChatOpenAI(model="gpt-4o", temperature=0.1)
        self.embeddings = embeddings if embeddings else OpenAIEmbeddings(model="text-embedding-ada-002")
        super().__init__(llm, embeddings, parser_llm, structured_llm, processor= processor)

        if not properties:
            self.properties = PROPERTIES
        else:
            self.properties = properties
            
        pass
    
    def extraction_CoV(
            self,
            MOF: str,
            vector_store,
            specific_properties: List[str],
            read_prompts = List[str],
            verification_prompts = List[str],
            recheck_prompts = List[str],
            ret_docs: bool = False):

        """This is the extraction with Chain of Verification (CoV) function. It takes a more vigorous path to find the correct output.
        
        Use must specify the list of specific properties they are looking for. They must then also provide the following:
            -Property-specific read-prompts list
            -List of verification prompts for every specific property
            -List of recheck prompts for every specific property

        Note: the properties filter is not used in this function!
        
        The return is a tuple of length 2 containing the following:
            -List of properties with the same length as specific_properties. This is not a PropertyList object, it is simply a list of Property objects!
            -All of the text that the LLM looked through to find the output. This is None if ret_docs is False
        """
        
        if len(specific_properties) != len(read_prompts) or \
            len(specific_properties) != len(verification_prompts) or \
            len(specific_properties) != len(recheck_prompts):
            print("The lengths of read_prompts, verification_prompts and recheck_prompts must be the same as the number of properties given in specific_properties.")
            raise AssertionError()

        specific_property_return = []
        parser = self.Parse_Output(Property)
        verification_parser = self.Parse_Output(Verification)
        names = " ---".join([f"name {i+1}: {name.replace('{', ']').replace('}', ']')}" for i, name in enumerate(MOF.split("<|>"))])
        
        for i, specific_property in enumerate(specific_properties):

            print(f"Reading to find the {specific_property} of {MOF} specifically")
            (property, docs) = self.RAG_Chain_Output(read_prompts[i].format(MOF_name=names), vector_store, pydantic_output=Property)
            property.condition = ""
            property.name = specific_property
        
            print("LLM Structured Output: ")
            print(property)
        
            if (property.value.lower() == "not provided"):
                print(f"\nCould not find the {specific_property} in the document")
                specific_property_return.append(property)
                continue

            print("\nVerifying the extraction:")

            verification = verification_parser.invoke(verification_prompts[i].format(output=property, Property_name=specific_property, MOF_name=names))

            if(verification.valid):
                specific_property_return.append(property)
                continue

            print("\nReading the document again to find a different justification/label")

            (property, docs) = self.RAG_Chain_Output(recheck_prompts[i].format(MOF_name=names, Property_name=specific_properties[i], label=property.value, sent=property.summary), vector_store, pydantic_output=Property)
            property.condition = ""
            property.name = specific_property

            print("LLM Structured Output from Rechecking: ")
            print(property)

            specific_property_return.append(property)

        if ret_docs:
            return specific_property_return, docs
        else:
            return specific_property_return, None
    

    def property_extraction(
            self,
            MOF: str,
            read_prompt: str,
            vector_store,
            ret_docs: bool = False,
            structured_output: BaseModel = PropertyList):
        
        parser = self.Parse_Output(structured_output)

        print("Action: reading the document")
        names = " ---".join([f"name {i+1}: {name.replace('{', '[').replace('}', ']')}" for i, name in enumerate(MOF.split("<|>"))])
        print(f"finding all properties of {names}")

        (answer1, docs) = self.RAG_Chain_Output(read_prompt.format(MOF_name=names), vector_store)

        print("\nResult: ")
        print(answer1["answer"])

        list_properties = parser.invoke(f"Parse the following text into the structured output\nText:\n{answer1['answer']}")

        print("\nParsed Result: ")
        print(list_properties)
        print("\n")

        return (list_properties, docs) if ret_docs else list_properties

    def agent_response(
            self,
            MOF: str,
            paper_file_name: str,
            read_prompt: str,
            specific_properties: List[str] = None,
            specific_properties_prompts: Dict[str, List[str]] = None,
            vector_store: Optional[str|FAISS] = None,
            local_vector_store_embeddings: Optional[str] = None,
            ret_docs: bool = False,
            store_vs: bool = False,
            CoV: bool = False,
            skip_general: bool = False,
            gen_extraction_structure: BaseModel = PropertyList):
        
        if not vector_store:
            vector_store = self.create_vector_store(paper_file_name, store_vs=store_vs)
        elif type(vector_store) is str:
            if path.isdir(vector_store):
                vector_store = FAISS.load_local(vector_store, local_vector_store_embeddings if local_vector_store_embeddings else self.embeddings, allow_dangerous_deserialization=True)
            else:
                vector_store = self.create_vector_store(paper_file_name, store_vs=store_vs, store_folder=vector_store)

        general_response = None

        if not skip_general: 
            general_response = self.property_extraction(MOF, read_prompt, vector_store, ret_docs, gen_extraction_structure)

        if CoV:
            specific_resposne = self.extraction_CoV(MOF, vector_store, specific_properties, **specific_properties_prompts, ret_docs=ret_docs)
            return general_response, specific_resposne
        
        return general_response
