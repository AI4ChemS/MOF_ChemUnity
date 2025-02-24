RULES_WATER_STABILITY = """
There are only 2 options for water stability (Stable, Unstable):
1. Stable:  -retains properties/porous structure/crystallinity after exposure to water/steam/humidity.
            -Insoluble in water or an aqueous solution.
            -Water adsorption isotherm has a steep uptake.
            -Good cycling performance.

2. Unstable:
            -The MOF will decompose/change properties/change crystal structure after exposure to water/steam/humidity
            -Soluble or patrially soluble in water or an aqueous solution.

3. Not provided:    -No information provided for either label
                    -Any thermal analysis or thermal reactions are not water stability.
                    -In-Air Decomposition or Instability of crystal unless humidity is mentioned
                    -Any mention of TGA or TG or temperature is not considered water stability even if water molecules are involved
                    -Information about the interaction with Organic solvents other than including water
"""

VERF_RULES_WATER_STABILITY = """Check on steep uptakes, solubility in water, change in properties after being exposed to water/steam, change in crystallinity, or mention of water stability in the sentence.
Now, is the justification for the previous extracted label valid?

Do not make up answers.
Do not consider chemical or thermal stability (including TGA or any testing under varying temperatures) or stability in air as a valid reason."""

WATER_STABILITY = """You are an expert chemist. In the document find the Water Stability of the MOF with the following Names and Coreferences: {MOF_name}. 
Use the following rules to determine its water stability:
{RULES}

DO NOT HALLUCINATE!
Your final answer should contain the following:
    1. The water stability of the MOF. 
    2. The exact sentences without any changes from the document that justifies your decision. Try to find more than once sentence. This should be "Not provided" if you cannot find water stability.


Examples: -Documents: "The MOF is found to dissociate only in methanol but is otherwise insoluble in water which is due to highly polar ions or something"
          1.Correct Label:  "Stable"
          2.The MOF is found to dissociate only in methanol but is otherwise insoluble in water

          -Documents: "The MOF is insoluble in water and common organic solvents. It has a very unique shape and an interesting geometry..."
          1.Correct Label: "Stable"
          2.The MOF is insoluble in water and common organic solvents.

          -Documents: "This MOF is found to be insoluble in water. After immersion in water the PXRD showed a shift in the peaks. This indicates some changes to the crystals"
          1.Correct Label: "Unstable"
          2.After immersion in water the PXRD showed a shift in the peaks. This indicates some changes to the crystals

          -Documents: "To get the diffractions, the MOF was dissolved in organic solvents. The thermal analysis and TGA showed interesting isotherms for this MOF."
          1.Correct Label: "Not Provided"
          2.There is not mention of water, steam, or humidity any where in the documents. 
"""

WATER_STABILITY_RE = """This time, you must change the label or find a different VALID justification (Say "Not provided" if you cannot do either).
Use the following rules to determine its water stability usin VALID justifications:
{RULES}

Please do not hallucinate. You need to change your previous output
Your final answer should contain the following:
    1. The new water stability label of the MOF.
    2. The new exact sentences without any changes from the document that justifies your decision. Try to find more than once sentence.

Examples: -Documents: "There is no clear crystals obtain for this MOF when dissolved in DMF. The PXRD shows no diffraction to be noted and no peaks. The weight loss in TGA is mainly due to water molecules leaving the crystal. The MOF is found to be water insoluble"
          -Previous Output: Label -> Unstable, Justification -> The weight loss in TGA is mainly due to water molecules leaving the crystal.
          1.Correct Label: "Stable"
          2.The MOF is found to be water insoluble.

          -Documents: "The MOF retains its crystal structure when immersed in H2O, MeOH and EtOH. However, there is a clear change in color and crystallinity when dissolved in other organic solvents like DMSO or DMF."
          -Previous Output: Label -> Unstable, Justification -> The MOF retains its crystal structure when immersed in H2O, MeOH and EtOH.
          1.Correct Label: "Stable"
          2.The MOF retains its crystal structure when immersed in H2O, MeOH and EtOH.

          -Documents: "The MOF is thermally tested and we found that water molecules exit the structure first with weight loss of 1.9% which is later shown in the TGA analysis."
          -Previous Output: Label -> Unstable, Justification -> The MOF is thermally tested and we found that water molecules exit the structure first with weight loss of 1.9%
          1.Correct Label: "Not provided"
          2.There is no mention of stability of the MOF in water
"""