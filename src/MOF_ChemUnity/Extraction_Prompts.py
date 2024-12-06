EXTRACTION = """You are an expert in coordinated chemistry and Metal Organic Frameworks (MOF).
You need to extract relevant physical, chemical and structural properties for a MOF that has the following names: {MOF_name}.
Please be precise and try to be as accurate as possible. Make sure all properties are related ONLY to the MOF Names provided.

Your output should have the following format for each property and its value:
1.  -Property Name: the name of the extracted property. Be consistent and use field relevant names. Do not include units here.
    -Property Value: the value for the property, please be precise and do not include units here, you need to fix any formatting issues.
    -Value Units: the units for this property. Include percentages, letters and signs that refer to units. You need to fix any formatting issues.
    -Conditions: the experimental conditions that this value was observed at.
    -Summary: The exact sentences from the provided text that mention the MOF Name and this property."""

VERIFICATION = """You are an expert in chemistry. Do the below justification sentences actually talk about the {Property_name} of the {MOF_name}?

Extracted Output: {output}

{VERF_RULES}

Start your answer clearly with "Valid" or "Invalid".
"""

RECHECK = """You are an expert chemist. In the document find the {Property_name} of the MOF with the following Names and Coreferences: {MOF_name}.
Your previous output is incorrect, find a different justification and/or label (you cannot use your previous output or base your answer on the same sentences as the previous output; use "not provided" if you cannot find anything else)

Previous Extraction:
1. Water stability of the MOF: {label}
2. Justification sentences: {sent}

{RECHECK_INSTRUCTIONS}
"""