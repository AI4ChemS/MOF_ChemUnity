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

APPLICATION = """You are an expert in coordinated chemistry and Metal Organic Frameworks (MOF). This document below talks about different MOFs. I need you to help find the application for the following single MOF and its Coreferences" {MOF_name}.
Please extract the application that the author mentions in the documents. The application is a classification for a material or a general field of application of materials. 
Try to use field-related applications, for example, do not say gas adsorption. Instead specify which gas.
Do not hallucinate please. Studies on specific properties are not applications.

You have the following options for output:

1. If you find applications, format the output with the following:
    1.  -Application: The application that the authors say this MOF is being investigated/recommended for. If not found, say "Not Provided"
        -Recommendation: Is the MOF good in this application or bad. If the authors say that this MOF is good for the application, say RECOMMENDED. If it is bad, say NOT RECOMMENDED. If the authors do not mention a recommendation, then say INVESTIGATED. This should say "Not Provided" if the application is not provided.
        -Justification: You need to extract the exact sentences from the documents that mention the application. And the sentences that provide the recommendation """