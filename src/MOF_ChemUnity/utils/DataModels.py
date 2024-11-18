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
    summary: str = Field(description="the original text that talks about this property")

    def __str__(self):
        compiled_string = ""

        compiled_string += f"{self.name} = {self.value}{self.units if self.units.lower() != 'none' else ''}"
        compiled_string += f" ; conditions: {self.condition if self.condition.lower() != 'none' else ''}"
        compiled_string += f" ; Justification: {self.summary}"

        return compiled_string

class PropertyList(BaseModel):
    properties: List[self.Property]

    def __str__(self):
        compiled_string = ""

        for i, prop in enumerate(self.properties):
            compiled_string += f"{i+1}- {prop}\n"
        
        return compiled_string

class Verification(BaseModel):
    valid: bool = Field(description="Whether the output indicates a valid (true) or invalid (false)")