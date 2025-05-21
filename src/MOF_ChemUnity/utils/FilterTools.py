import pandas as pd
from thefuzz import fuzz


def filter_and_standardize(df: pd.DataFrame, which: str, mapper: dict,  threshold: int = 80):
    used_keys = []

    df_copy = df.copy(deep=True)
    df_copy[f"Original {which} Name"] = df_copy[which]
    current_code = df_copy.loc[0, "Ref Code"]

    for j in range(len(df_copy)):
        if current_code.lower() != df_copy.loc[j, "Ref Code"].lower():
            current_code = df_copy.loc[j, "Ref Code"]
            used_keys = []
        
        maximum_match = "none"
        maximum_score = 0
        for k, v in mapper.items():

            for i in v:
                score = fuzz.ratio(df_copy.loc[j, which].lower(), i.lower())

                if score >= threshold and score > maximum_score:
                    maximum_score = score
                    maximum_match = k
        
        if maximum_score >= threshold:
            if maximum_match.lower() != "remove":
                used_keys.append(maximum_match)
        
        df_copy.loc[j, which] = maximum_match

    
    return df_copy