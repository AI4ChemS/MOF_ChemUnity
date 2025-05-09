MATCH_REFCODES = """You are an expert chemist. The document describes the synthesis and characterization of Metal-Organic Frameworks (MOFs) and Coordinated Polymers (CPs) with crystal structures and other properties. MOFs or CPs are compound with very well-defined crystalline structure that consist of a transition metal node like Cu, Dy, Zn, etc. and an organic linker that is commonly referred to with short hand names like DME, or BTC. Use your chemistry knowledge to determine whether a compound is a metal, organic linker or a MOF.

## Instructions:
1) Compound names: MOFs and CPs can have different based on the author. They can be code names like: 'ZIF-8, HKUST-1, etc.' or Chemical formulas: 'Cu2(btc)3, etc.' Make sure to extract one of these formats after resolving any co-references such as 'Compound 1, 1a, crystal 1, network 1a, etc'. When outputting the final MOF name, concatenate the all co-references to the single MOF with "<|>". For Example, "Cu2(Btc)3 - HKUST-1, or compound 1, is a very good MOF". Should output a MOF name of "Cu2(BTC)3<|>HKUST-1<|>compound 1". The MOF names you are extracting MUST BE UNQIUE!

2) Make sure to fully unpack MOF generic formulas into the individual MOFs names. For example "X-DMF.2H2O (X = Cu, Zn, Mn)" should output MOFs 'Cu-DMF.2H2O', 'Zn-DMF.2H2O', 'Mn-DMF.2H2O'. Often you can encounter co-references their as well. For example, "Cu2(DMF)4.3(S) (S = iba (Cu-iba), ina (Cu-ina))" should output the following individual MOFs: 'Cu2(DMF)4.3(iba)<|>Cu-iba' and 'Cu2(DMF)4.3(ina)<|>Cu-ina'.

3) Justification: Always provide a justification for your output. The justification must be logical and should help the user understand how you went about answering their question. Never make up answers without justification from provided information. You can use chemistry knowledge to deduce Metal Nodes and Organic Linkers and chemical formula stoichiometry only!

4) Always include the following in the output: DOI, MOF Name from text, CSD Reference Code (if Provided). Do not use CCDC Reference Codes for the papers.

## Task:
I have the following CSD Reference codes for MOFs. Only use these Ref Codes:

{csd_ref_codes}

You need to find which MOFs in the provided text have these CSD Reference codes. Use the features provided for each CSD reference code like Lattice Parameters (a, b, c), Metal node, Chemical Name, Space group, Molecular formula, and Synonyms to find the matching MOF from the paper. Do not hallucinate information not included in the paper.
EACH MOF CAN HAVE A SINGLE REF CODE AT MOST
YOU MUST USE THE FOLLOWING FORMAT FOR EACH MOF YOU FIND:
1.  -MOF name: name of the MOF along with the co-references concatenated with '<|>'. These names must be unique! Unpack generic formulas
    -CSD Ref Code: the CSD Ref Code for the specific MOF. Use "not provided" if you believe non of the MOFs match any CSD Ref Code. Don't over use 'not provided'
    -Justification: why do you believe this MOF has this CSD Ref Code. Explain whether Metal node, space group, molecular formula or organic linker match.
"""

MATCH_REFCODES_SHORT = """You are an expert in coordination chemistry and coordinated compounds.
This document discusses the synthesis, characterization and properties of Metal-Organic Frameworks (MOF). 
MOFs are a type of coordinated compounds that consists of the following:
    -Metal Node: Typically a transition metal like Cu, Zn, Sm, etc. This has to be a valid metal element.
    -Organic Linker: This is an organic ligand that coordinates with the metal nodes. These organic ligands can be functionlized with different functional groups.
    -Solvent/Water Complex: Often, these are entraped within the crystal formed

I have the following CSD Reference Codes for the MOFs mentioned in this document, and I need help matching each Reference Code to the MOF Name in the document:

{csd_ref_codes}

Your output should follow the following format for each MOF reported with a matching CSD Ref Code:
1.  -MOF name: the name of the MOF and ts co-references concatenated with <|>. You cannot have multiple MOFs with the same name. Get the full name (e.g compound 1, complex 3, etc.)
    -CSD Reference Code: The matching CSD Reference Code. You should not use the same CSD Reference Code more than once.
    -Justification: Single sentence explaining why the MOF matches with this CSD Reference Code"""

CHECK_JUSTIFICATION = """Do the below sentences actually explain why the MOF has the corresponding CSD Reference Code.
A 'Valid' justification explains how there is matching Metal Nodes, Space Group or Molecular Formula. When comparing Molecular formulas, keep in mind that you can encounter an empirical formula.
Try to figure out whether the stoichiometry is the same between the CSD Molecular Formula and the report Formula. If so, then you can be more confident that you have a match.
Only 2 out of 3 need to match. The justification simply needs to be satisfying with 30% probability. If you have 2 matches and more than 30% probability, then output 'Valid', otherwise, 'invalid'

Evaluate the justification for the following MOF: {MOF_info}
Currently, the CSD Ref Code and CSD Information for this MOF are: {CSD_info}
Justification: "{MOF_justification}"

Relavant Documents:
{relavant_docs}
"""

CHECK_JUSTIFICATION_SHORT = """Does this MOF match with this/these CSD Reference Code:
MOF: {MOF_info}
CSD Reference Code and Information: {CSD_info}
Original Justification: {MOF_justification}"""

RECHECK = """The document describes various characteristics of {MOF_name}. Find out which Ref Code matches with this MOF. 
You should also resolve incorrect naming of this MOF. For example, If the MOF name is "X-DMF<|>compound 2" and in the documents, 'compound 2 is the MOF with Sm metal node', then you need to update the MOF name to "Sm-DMF<|>compound 2".

Here are the CSD Ref Codes Again:
{csd_ref_codes}

Always include the following in the output: DOI, MOF Name from text, CSD Reference Code (if Provided) using the following format for each MOF:
"-MOF name: name of the MOF along with the co-references concatenated with '<|>'
 -CSD Ref Code: the CSD Ref Code for the specific MOF. Use "not provided" if you believe non of the MOFs match any CSD Ref Code. Don't over use 'not provided'
 -Justification: why do you believe this MOF has this CSD Ref Code. Explain whether Metal node, space group, molecular formula or organic linker match.
"""

EXTRACTION = """You are an expert in coordinated chemistry and Metal Organic Frameworks (MOF).
You need to extract relevant physical, chemical and structural properties for a MOF that has the following names: {MOF_name}.
Please be precise and try to be as accurate as possible. Make sure all properties are related ONLY to the MOF Names provided.

Your output should have the following format for each property and its value:
1.  -Property Name: the name of the extracted property. Be consistent and use field relevant names. Do not include units here.
    -Property Value: the value for the property, please be precise and do not include units here, you need to fix any formatting issues.
    -Value Units: the units for this property. Include percentages, letters and signs that refer to units. You need to fix any formatting issues.
    -Conditions: the experimental conditions that this value was observed at.
    -Summary: The exact sentences from the provided text that mention the MOF Name and this property."""

SYNTHESIS = """You are an expert in Coordination reactions and Metal-Organic Frameworks (MOF) synthsis.
I need you to help me extract synthesis information for a MOF that has the following names: {MOF_name}.
Please be as accurate as possible and provide a complete picture on how the synthesis of the MOF was carried out.

Your output should have the following format:
    -Synthesis Reaction Classification: The reaction classification, like solvothermal, coordination, etc.
    -Reagents Used: what reagents were used in this protocol.
    -Steps: the synthesis steps, with conditions, that were carried out in this synthesis.
    -Results: metrics about the reaction performance like Yield and Purity."""

RULES_WATER_STABILITY = """
There are only 3 options for water stability:
1. Stable:  -No change in properties after exposure to moisture or steam, soaking or boiling in water or an aqueous solution.
            -Retaining its porous structure in solution. 
            -No loss of crystallinity.
            -Insoluble in water or an aqueous solution.
            -Water adsorption isotherm should have a steep uptake.
            -Good cycling performance.

2. Unstable:
            -The MOF will decompose or change properties or has a change in its crystal structure after exposure/soak to a humid environment, steam or if it partially dissolves in water.
            -Soluble or patrially soluble in water or an aqueous solution.


3. Not provided: If you don't know or cannot justfy 1 or 2
"""

VERF_RULES_WATER_STABILITY = """To do this, you should check on steep uptakes, solubility in water, change in properties after being exposed to water/steam, change in crystallinity, or mention of water stability in the sentence.
If the justification can somehow imply water stability/instability, update "Water stability" to Stable/Unstable
Do not make up answers.
Do not consider chemical or thermal stability or stability in air as a valid reason."""

WATER_STABILITY = """You are an expert chemist. In the document find the Water Stability of the MOF with the following Names and Coreferences: {MOF_name}. 
Use the following rules to determine its water stability:
{RULES}

Your final answer should contain the following:
    1. The water stability of the MOF. 
    2. Testing conditions for water stability.
    3. The exact sentences without any changes from the document that justifies your decision. Try to find more than once sentence. This should be "Not provided" if you cannot find water stability.
"""

VERIFICATION = """Do the below justification sentences actually talk about the {Property_name} of the {MOF_name}?

Extracted Output: {output}

{VERF_RULES}

Start your answer clearly with "Valid" or "Invalid".
"""

RECHECK = """You are an expert chemist. In the document find the {Property_name} of the MOF with the following Names and Coreferences: {MOF_name}.
Previously, you suggested the following extraction which was INCORRECT:

Previous Extraction: {output}

{RECHECK_INSTRUCTIONS}
"""

WATER_STABILITY_RE = """This time, you must find a different justification and/or label for the water stability. Or say "Not provided" as outline by the rules below.
Use the following rules to determine its water stability:
{RULES}

Your final answer should contain the following:
    1. The water stability of the MOF. 
    2. Testing conditions for water stability.
    3. The exact sentences without any changes from the document that justifies your decision. Try to find more than once sentence. This should be "Not provided" if you cannot find water stability.
"""

FE_EXTRACTION = """You are an expert in electrochemistry. In the document, you need to identify the fradaic effeciency as a result of using this metal organic framework (MOF): {MOF_name}.
When reporting the faradaic effeciency, there are the following important factors:
    1. Identify the catalyst/MOF - this should have one of the following names: {MOF_name}
    2. Identify the specific product discussed - this important as each product has its own faradaic efficiency (eg. CH4, CO, CO2, C2H2, etc.)
    3. Report the faradaic efficiency (if it exists) for that specific product. It is typically mentioned as \"FE\" or \"FE\" subscript product.
    4. Find the associated voltage at which this faradaic efficiency is achieved, you may need to intrepret this from other chunks of text related to the specific MOF.
    5. Identify the reference electrode which is typicall reported as \"vs RHE\" or \"vs Ag/AgCl\", etc.

For each catalyst/MOF, there can be multiple product-Faradaic Efficiency Pairs

In the extraction, report the results for each unique product as follows:
    -Property Name: the name of the product + \"Faradaic Efficiency\" (for example, C2H4 Faradaic Efficiency)
    -Property Value: the value of faradaic efficiency (FE) associated with the product mentioned
    -Value Units: it has to be a percentage (%)
    -Conditions: this is going to be the voltage at which the faradaic efficiency for the product using the MOF is observed + the reference electrode
    -Summary: The exact sentences from the original text that contain the information above. Try to extract more than a single sentence"""

FE_VERIFICATION_RULES = """You need to determine whether the justification talks about {Property_name} of {MOF_name}. If it does not, then you should say that the justification is invalid.
Otherwise, you then will have to determine whether the output provided can be justified with the justification. If not, you should say invalid. Otherwise the justification is valid."""

FE_RECHECK = """You need to go over the document provided and find a better answer/justification for {Property_name} of {MOF_name}.

When reporting the faradaic effeciency, there are the following important factors:
    1. Identify the catalyst/MOF - this should have one of the following names: {MOF_name}
    2. Identify the specific product discussed - this is important as each product has its own faradaic efficiency (eg. CH4, CO, CO2, C2H2, etc.)
    3. Report the faradaic efficiency (if it exists) for that specific product. It is typically mentioned as \"FE\" or \"FE\" subscript product.
    4. Find the associated voltage at which this faradaic efficiency is achieved, you may need to intrepret this from other chunks of text related to the specific MOF.
    5. Identify the reference electrode which is typicall reported as \"vs RHE\" or \"vs Ag/AgCl\", etc.

For each catalyst/MOF, there can be multiple product-Faradaic Efficiency Pairs

In the extraction, report the results as follows:
    -Property Name: {Property_name}
    -Property Value: the value of faradaic efficiency (FE) associated with the product mentioned
    -Value Units: it has to be a percentage (%)
    -Conditions: this is going to be the voltage at which the faradaic efficiency for the product using the MOF is observed + the reference electrode
    -Summary: The exact sentences from the original text that contain the information above. Try to extract more than a single sentence"""

DENSITY_EXTRACTION = """You are an expert in metal-organic frameworks and reticular chemistry. In the document, you need to find the density of this metal-organic framework (MOF): {MOF_name}.

{RULES}

In the extraction, report the results as follows:
    -Property Name: Density
    -Property Value: the value for the density of the MOF. If you cannot find mention of density values in the paper, this should have value "Not Provided"
    -Value Units: these are the units that the document uses for density. They must be in units mass per volume.
    -Conditions: the conditions at which this value is observed
    -Summary: the exact sentences from the original text that contain the information above. Try to extract more than a single sentence. If they value was extracted from what looks like a table, report the table number as well."""

DENSITY_RULES = """Density of metal-organic frameworks is typically reported in a table. It is rare that you will find it in the main body of the paper. Density has units of mass per volume like: g/cm3 or g cm-3, etc. When looking for density, authors might use \u03c1c (\u03c1 subscript c) or Dp (D subscript p).
The units are typically available after these symbols (for example: Dp/ g cm-3). Therefore, when extracting density, make sure that the units are indeed mass per volume. The symbols used can be different from what is given here."""

DENSITY_VERIFICATION_RULES = """You need to determine whether the density extracted below is for this MOF. You also should check whether the units are mass per volume, if there are no units provided. Then the extraction is not valid.
You should also check whether the justification given talks about density and this MOF. If it does not talk about them, then the justification is invalid. 
The magnitude of density should be reasonable in the context of solid metal-organic frameworks and the units used. (For example, 10^6 g cm-3 does not make sense because that's too big. Neither does 10 kg m-3 because that is too small)

Here are the rules that guided the extraction:

{RULES}"""

DENSITY_RE = """This time, you must look for a different justification or different mention of density for this MOF. If you cannot find any other mention, return \"Not Provided \". Follow the rules below for help:

{RULES}

In the extraction, report the results as follows:
    -Property Name: Density
    -Property Value: the value for the density of the MOF. If you cannot find mention of density values in the paper, this should have value "Not Provided"
    -Value Units: these are the units that the document uses for density. They must be in units mass per volume.
    -Conditions: the conditions at which this value is observed
    -Summary: the exact sentences from the original text that contain the information above. Try to extract more than a single sentence. If they value was extracted from what looks like a table, report the table number as well.
"""