# MOF_ChemUnity
Knowledge graph database containing computational and experimental information for more than 15,000 metal-organic frameworks developed using large language models. For more details, please refer to our paper

# Prerequisites
MOF-ChemUnity uses Neo4J as the graph database engine. Installation instructions can be found [here](https://neo4j.com/pricing/). If interested in using python, please install the Neo4J python driver using

```bash
pip install neo4j
```

# Usage
Most users who are interested in querying the knowledge graph can simply import MOF-ChemUnity to their local Neo4J engine then use the `QueryAgent`. In this repository, you can find sample data in this [folder](https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/src/Examples/KG_Data/) as CSV files. Additionally, you can use [`neo4j_import.py`](https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/src/KnowledgeGraph/neo4j_import.py) to help import MOF-ChemUnity to your local instance of Neo4J.

You need to have the following CSV files **(Note - all files contain CSD reference code and DOI corresponding to the reference paper for each row)**:
| CSV File Name | Description |
| :-------------: | ----------- |
| matching.csv | Contains the MOF name associated with each CSD reference code from a given paper (DOI) |
| filtered_props.csv | Contains the properties extracted from literature  |
| applications.csv | Contains the applications for associated with each CSD reference code extracted from literature |
| synthesis.csv | Contains the synthesis protocols for each MOF extracted from a given paper |
| ws.csv | Contains the water stability for MOFs extracted from literature |

In your script, you can first set the environment variables to access Neo4J:

```python

import os

os.environ["NEO4J_URI"] = "your neo4j uri"
os.environ["NEO4J_USER"] = "your neo4j user name (should have read/write access)"
os.environ["NEO4J_PASSWORD"] = "your neo4j password"
```

Then you can import the data from CSV files into Neo4J using **(NOTE - the CSV files must be in the same folder that you are running the following script from!)**:

```python
from neo4j_import import run_queries

run_queries()
```
Once this is done, you should not run the previous steps again unless you have new data from new CSV files that you want to add to the knowledge graph.
At this point, you have a sample of MOF-ChemUnity available for you to use.

## Quick note on using this repository
The basic class used in this work is `BaseAgent` from which other agents may inherit specific functions. Each operation uses a specific agent and you will find an agent that performs any of the tasks presented in the work. `Base Agent` also allows more advanced users to create their own agents that perform customized tasks such as extracting other information from literature. More on that later.

## Querying the knowledge graph using QueryAgent
The easiest way to query the MOF-ChemUnity is to use the `QueryGenerationAgent`. You can find notebooks with demos in [this folder](https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/src/ChatGPT%20Comparison/) which query MOF-ChemUnity for various tasks including simply retrieval (task 4), prediction (task 1), inference (task 2) and recommendation (task 3). Using MOF-ChemUnity, it has been demonstrated that the query results are massively better in terms of quality (Q) and trustworthiness (T) for all of the tasks.

![GPTComparison](https://github.com/user-attachments/assets/6b3af877-df28-420b-a244-70c4dce9d2d4)

With that, to query MOF-ChemUnity all you need is the following 3 lines of code:

```python
from MOF_ChemUnity.Agents.QueryAgent import QueryGenerationAgent

# Connects to graph using environment variables (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
agent = QueryGenerationAgent()

# Return a Pandas DataFrame
query_result = agent.run_full_query("your question about MOFs in MOF-ChemUnity")
```

# Main
MOF-ChemUnity is a knowledge graph which combines the available computational information for MOFs and the experimental information within literature in a single database. Computational information includes computed geometric descriptors (using Zeo++), [revised autocorelations (RACs)](ref), and available gas uptake labels and electronic properties from [CoRE-MOF](ref) and [QMOF](ref), respectively. The experimental information was extracted automatically using Large Language Models (LLMs), specifically, GPT-4o. Extracted information includes MOF names, properties, applications, and synthesis protocols mentioned in the literature. Finally, all data is linked together using CSD reference codes. In other words, you can find MOFs using their name or their CSD reference code as this database features a one-to-one link between them. 

## What can you do with MOF-ChemUnity
MOF-ChemUnity enables improved querying performance when asking GPT-4o questions about MOFs (See image above). It also includes a wide variety of information that was not easily available before like applications and seemingly links this information to available computation labels via CSD reference codes. This enables finding MOFs similar to other MOFs as shown in [this demo](link to demo). 

## Can more information be included
Absolutely! In [this demo](link to cross-document demo) we show how the MOF names can allow users to use indexing libraries like CrossRef or Web of Science to find related papers that further explore the MOF. Then, they can extraction workflows and append the extracted data to MOF-ChemUnity. Additionally, new MOFs can also be added by running the [matching notebook](https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/src/ChemUnity_Matching.ipynb) then the [extraction notebook](https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/src/ChemUnity_Extraction.ipynb).

# Citation
```bibtex
@article{yettobedecided,
title = {idk yet},
author = {Aswad, Amro and Pruyn, Thomas and Khan, Sartaaj Takrim and Black, Robert and Moosavi, Seyed Mohamad},
year = {2025},
journal = {},
doi = {},
url = {},
note = {},
}
```

# Privacy
We do not collect any user information in this work. You must use your own OpenAI API key and we do not store nor see any inputs or outputs.

# Full Data Availability
For copyright reasons, the complete dataset is not hosted. Please contact [mohamad.moosavi@mail.utoronto.ca](mohamad.moosavi@mail.utoronto.ca) for the full data and project collaborations.

# Credits
This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.


