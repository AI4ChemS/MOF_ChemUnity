SYNTHESIS_EXTRACTION = """
You are an expert in reticular chemistry and Metal-Organic Frameworks (MOF).
Your job is to extract details about the synthesis procedure for a MOF that has the following names: {MOF_name}
Please be precise and as accurate as possibile. Make sure the synthesis details pertain to ONLY the MOF Names provided. If you cannot find the synthesis details for a given MOF, report that detail as "Not Provided".

Your output should have the following format: 
1. - Metal Precursor: The name of the metal precursor(s) used in the synthesis. Ensure the names are chemically correct and formatted properly.
   - Solvent: The solvent(s) used in the synthesis process. Include all relevant solvents and their ratios if provided.
   - Temperature: The temperature at which the synthesis was conducted. If a temperature range is provided, include it.
   - Reaction Time: The duration for which the synthesis reaction was carried out. Include units and correct formatting.
   - Synthesis Procedure: A detailed step-by-step description of how the MOF was synthesized. Ensure clarity and accuracy.
   - Additional Conditions: Any other experimental parameters mentioned, such as pH, pressure, additives, or special conditions.
   - Justification: The exact sentences from the provided text that describe the synthesis procedure for this MOF.

"""
