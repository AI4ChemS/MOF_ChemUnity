import os
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase
from openai import OpenAI
from MOF_ChemUnity.Prompts.Query_Generation_Prompts import TEXT_TO_CYPHER  # alignment prompt no longer used
from IPython.display import display as ipy_display

class QueryGenerationAgent:
    """Single‑step NL ➜ Cypher generator that passes a JSON schema to GPT‑4o."""

    def __init__(self, neo4j_uri=None, neo4j_user=None, neo4j_password=None):
        load_dotenv()
        self.NEO4J_URI  = neo4j_uri  or os.getenv("NEO4J_URI")
        self.NEO4J_USER = neo4j_user or os.getenv("NEO4J_USER")
        self.NEO4J_PASSWORD = neo4j_password or os.getenv("NEO4J_PASSWORD")
        if not all([self.NEO4J_URI, self.NEO4J_USER, self.NEO4J_PASSWORD]):
            raise ValueError("Missing Neo4j credentials (URI / USER / PASSWORD).")

        # connect
        self.driver = GraphDatabase.driver(self.NEO4J_URI, auth=(self.NEO4J_USER, self.NEO4J_PASSWORD))
        with self.driver.session() as s:
            s.run("RETURN 1")
        print("✅ Connected to Neo4j.")

        self.client = OpenAI()

    # ---------- low‑level helpers ----------
    def run_cypher_query(self, query: str):
        with self.driver.session() as s:
            return [r.data() for r in s.run(query)]

    # ---------- schema helpers ----------
    def _fetch_node_schema(self):
        q = """
        MATCH (n)
        WITH labels(n)  AS lbls, keys(n) AS props
        WITH apoc.text.join(lbls,":") AS label, collect(props) AS prop_lists
        WITH label, reduce(s = [], x IN prop_lists | s + x) AS flat
        RETURN label AS node, collect(DISTINCT flat) AS props
        """
        res = self.run_cypher_query(q)
        return {row['node']: sorted(set().union(*row['props'])) for row in res}

    def _fetch_rel_schema(self):
        rel_types = [r['relationshipType'] for r in self.run_cypher_query("CALL db.relationshipTypes()")]
        out = {}
        for rel in rel_types:
            q = f"""
            MATCH ()-[r:`{rel}`]->() WITH keys(r) AS k LIMIT 100 UNWIND k AS key RETURN DISTINCT key
            """
            keys = [row['key'] for row in self.run_cypher_query(q)]
            out[rel] = sorted(keys)
        return out

    def _fetch_property_names(self):
        rows = self.run_cypher_query("MATCH (p:Property) RETURN DISTINCT p.name AS n")
        return sorted(r['n'] for r in rows)

    def _fetch_application_names(self):
        rows = self.run_cypher_query("MATCH (a:Application) RETURN DISTINCT a.name AS n")
        return sorted(r['n'] for r in rows)

    def _schema_json(self):
        return {
            "nodes": self._fetch_node_schema(),
            "relationships": self._fetch_rel_schema(),
            "propertyNames": self._fetch_property_names(),
            "applicationNames": self._fetch_application_names()
        }

    # ---------- NL ➜ Cypher ----------
    def generate_cypher(self, nl_query: str) -> str:
        schema_json = self._schema_json()
        messages = [
            {"role": "system", "content": TEXT_TO_CYPHER},
            {"role": "system", "content": json.dumps(schema_json)},
            {"role": "user",   "content": nl_query.strip()}
        ]
        resp = self.client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0)
        cypher = resp.choices[0].message.content.strip()
        # strip accidental code fences
        cypher = cypher.strip().lstrip('`').rstrip('`').strip()
        return cypher

    # ---------- public helpers ----------
    def run_full_query(self, nl_query: str):
        cypher = self.generate_cypher(nl_query)
        df = __import__('pandas').DataFrame(self.run_cypher_query(cypher))
        if df.empty:
            print("⚠️ No results found.")
        else:
            ipy_display(df)
        return df

    def print_schema(self):
        import pprint
        pprint.pprint(self._schema_json(), compact=True)

    def close(self):
        self.driver.close()
