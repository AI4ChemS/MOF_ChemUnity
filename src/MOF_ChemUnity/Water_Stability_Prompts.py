RULES_WATER_STABILITY = """
There are only 3 options for water stability:
1. Stable:  -Insoluble in water or an aqueous solution (ignore temperature dependence)
            -Retaining its porous structure in solution. 
            -No loss of crystallinity.
            -No change in properties after exposure to moisture or steam, soaking or boiling in water or an aqueous solution.
            -Water adsorption isotherm should have a steep uptake.
            -Good cycling performance.

2. Unstable:
            -The MOF will decompose or change properties or has a change in its crystal structure after exposure/soak to a humid environment, steam or if it partially dissolves in water.
            -Soluble or patrially soluble in water or aqueous solution.


3. Not provided:    -Stability or instability in air without clear mention of humidity or water
                    -If you don't know or cannot extract a jusification that implies 1 or 2.
                    -Any thermal analysis is not water stability.
                    -Any mention of TGA or TG or temperature is not considered water stability even if water molecules are involved
                    -Organic solvents or solutions with of water with other chemicals do not provide water stability label
"""

VERF_RULES_WATER_STABILITY = """To do this, you should check on steep uptakes, solubility in water, change in properties after being exposed to water/steam, change in crystallinity, or mention of water stability in the sentence.
If the justification is using organic solvents, highly acidic/basic/saline solutions, or organic-water solution to justifiy water stability or instability, then the label is not valid!
Do not make up answers.
Do not consider chemical or thermal stability (including TGA or any testing under varying temperatures) or stability in air as a valid reason."""

WATER_STABILITY = """You are an expert chemist. In the document find the Water Stability of the MOF with the following Names and Coreferences: {MOF_name}. 
Use the following rules to determine its water stability:
{RULES}

DO NOT HALLUCINATE!
DO NOT CONTRADICT THE AUTHORS!
If the authors say that the MOF is insoluble in water and there is no other evidence that indicates water unstable according to the rules, then the MOF is stable!
You are only asked to extract the information from text and be faithful to the documents!
Your final answer should contain the following:
    1. The water stability of the MOF. 
    2. The exact sentences without any changes from the document that justifies your decision. Try to find more than once sentence. This should be "Not provided" if you cannot find water stability.
"""

WATER_STABILITY_RE = """This time, you must find a different justification and/or label for the water stability. Or say "Not provided" as outline by the rules below.
Use the following rules to determine its water stability:
{RULES}

DO NOT HALLUCINATE!
DO NOT CONTRADICT THE AUTHORS!
If the authors say that the MOF is insoluble in water and there is no other evidence that indicates water unstable according to the rules, then the MOF is stable!
You are only asked to extract the information from text and be faithful to the documents!
Your final answer should contain the following:
    1. The water stability of the MOF.
    2. The exact sentences without any changes from the document that justifies your decision. Try to find more than once sentence.
"""