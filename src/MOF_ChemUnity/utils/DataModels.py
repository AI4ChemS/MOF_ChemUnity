from pydantic import BaseModel, Field
from typing import List, Optional

class MOFRefCode(BaseModel):
    name: str = Field(description="the name of the MOF with co-refences concatenated with '<|>'")
    refcode: str = Field(description="The CSD Reference Code for the MOF mentioned")
    justification: str = Field(description="justification sentences that talk about why the MOF has that CSD Reference Code. Should have value 'Not provided' if none of the CSD Ref Codes match with this MOF")

class MOFRefCodeList(BaseModel):
    mofs: List[MOFRefCode]

class RefCodeJustification(BaseModel):
    correct: bool = Field(description="whether the justification explains why the MOF has the corresponding Ref Code")

class Property(BaseModel):
    name: str = Field(description="the name of the property")
    value: str = Field(description="the value of the property. Saved as text!")
    units: str = Field(description="the units associated with the value for this property")
    condition: str = Field(description="the condition at which the value is observe/collected")
    summary: str = Field(description="the quotes from the original text that talk about this property")

    def __str__(self):
        compiled_string = ""

        compiled_string += f"{self.name} = {self.value}{self.units if self.units.lower() != 'none' else ''}"
        compiled_string += f" ; conditions: {self.condition if self.condition.lower() != 'none' else ''}"
        compiled_string += f" ; Justification: {self.summary}"

        return compiled_string

class PropertyList(BaseModel):
    properties: List[Property]

    def __str__(self):
        compiled_string = ""

        for i, prop in enumerate(self.properties):
            compiled_string += f"{i+1}- {prop}\n"
        
        return compiled_string

class Verification(BaseModel):
    valid: bool = Field(description="Whether the output indicates a valid (true) or invalid (false)")

class Application(BaseModel):
    application_name: str = Field(description="The application name that is found for the MOF. This should be as breif as possible. Do not use acronyms or abreviations without the full name")
    recommendation: str = Field(description="This the author recommendation, NOT YOURS. Can be one of the following values: Recommended, Not Recommended, Investigated, Not Provided")
    justification: str = Field(description="All of the exact sentences that were used to obtain the knowledge and answer the user questions about the application and recommendation")

    def __str__(self):
        return f"Application: {self.application_name}\nAuthor Recommendation: {self.recommendation}\nExact Sentences: {self.justification}"
    
class Synthesis(BaseModel):
    metal_precursor: str = Field(description="The name of the metal precursor(s) used in the synthesis")
    organic_linker: str = Field(description="The name of the organic linker used in the MOF's synthesis")
    solvent: str = Field(description="The name of the solvent used in the synthesis. Include all relevant solvents and their ratios if provided.")
    temperature: str = Field(description = "The temperature at which the synthesis was conducted. Include the units as well.")
    reaction_type: str = Field(description = "The general synthesis method used, such as solvothermal, hydrothermal, mechanochemical, etc. Include all types mentioned, in order.")
    reaction_time: str = Field(description = "The duration for which the synthesis reaction was carried out. Include units and correct formatting.")
    synthesis_procedure: str = Field(description = "A summarized step-by-step description of how the MOF was synthesized. Be as brief as you can without missing any key details.")
    additional_conditions: str = Field(description = "Any other experimental parameters mentioned, such as pH, pressure, additives, or special conditions. Be as brief as you can without missing any key details.")
    justification:str = Field(description = "All of the exact sentences that were used to obtain the knowledge and answer the user questions about the application and recommendation")
    def __str__(self):
        return f"Metal Precursor: {self.metal_precursor}\nOrganic Linker: {self.organic_linker}\nSolvent: {self.solvent}\nTemperature: {self.temperature}\nReaction Type: {self.reaction_type}\nReaction Time: {self.reaction_time}\nSummarized Procedure: {self.synthesis_procedure}\nAdditional Conditions: {self.additional_conditions}\nExact Sentences: {self.justification}"

class ListApplications(BaseModel):
    app_list: List[Application]

    def __str__(self):
        compiled_string = ""

        for i, app in enumerate(self.app_list):
            compiled_string +=f"{i+1}- {app}\n"
        
        return compiled_string
