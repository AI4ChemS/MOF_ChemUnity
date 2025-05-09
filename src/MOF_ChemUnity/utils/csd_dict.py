import pandas as pd
import glob
import os

def csd_dict(csd_data): 
    return {
        i["CSD code"]: {
            'Space Group': i["Space group"],
            'Metal Nodes': i["Metal types"],
            'Chemical Name': i["Chemical Name"],
            'a': i["a"],
            'b': i["b"],
            'c': i["c"],
            'Molecular Formula': i["Molecular formula"],
            'Synonyms': i["Synonyms"]
        } 
        for _, i in csd_data.iterrows()
    }