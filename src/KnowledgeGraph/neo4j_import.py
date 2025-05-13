from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import pandas as pd

# ==== CONFIG ====
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# === File paths ===
DESCRIPTOR_CSV = "ChemUnity_all_descriptors.csv"
MATCHING_CSV = "matching_results.csv"
EXPERIMENTAL_CSV = "filtered_properties_v3.csv"
WATER_CSV = "water_stability_filtered.csv"
APPLICATIONS_CSV = "applications_filtered_v3.csv"
SYNTHESIS_CSV = "synthesis_extractions.csv"
CSD_CSV = "CSD_Info_desc.csv"

load_dotenv()
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def batch_run(session, query, rows, batch_size=1000):
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        session.run(query, {"rows": batch})

def print_graph_stats(session):
    labels = ["MOF", "Property", "Application", "Reference", "MOF_Name"]
    for label in labels:
        count = session.run(f"MATCH (n:{label}) RETURN count(n) AS count").single()["count"]
        print(f"   {label}s: {count}")

def create_indexes(session):
    index_queries = [
        "CREATE INDEX IF NOT EXISTS FOR (m:MOF) ON (m.refcode)",
        "CREATE INDEX IF NOT EXISTS FOR (r:Reference) ON (r.doi)",
        "CREATE INDEX IF NOT EXISTS FOR (n:MOF_Name) ON (n.name)",
        "CREATE INDEX IF NOT EXISTS FOR (p:Property) ON (p.name)",
        "CREATE INDEX IF NOT EXISTS FOR (a:Application) ON (a.name)"
    ]
    for q in index_queries:
        session.run(q)

def run_queries():
    with driver.session() as session:
        create_indexes(session)

        print("\n📊 BEFORE IMPORT:")
        print_graph_stats(session)

        # === 1. MATCHING RESULTS ===
        print("\n🔄 Importing matching_results.csv...")
        df_match = pd.read_csv(MATCHING_CSV)
        rows = []
        for _, row in df_match.iterrows():
            for name in str(row["MOF Name"]).split("<|>"):
                if str(row["CSD Ref Code"]).lower() in ["not provided", "not applicable"]:
                    continue
                if name.lower().strip() in ["not provided", "not applicable"]:
                    continue
                rows.append({
                    "refcode": row["CSD Ref Code"],
                    "doi": row["DOI"],
                    "name": name.strip()
                })
        query = """
            UNWIND $rows AS row
            MERGE (m:MOF {refcode: row.refcode})
            MERGE (r:Reference {doi: row.doi})
            MERGE (m)-[:has_source]->(r)
            MERGE (n:MOF_Name {name: row.name})
            MERGE (m)-[:has_name]->(n)
            MERGE (n)-[:has_source]->(r)
        """
        batch_run(session, query, rows)
        print("✔ Done matching_results.csv")

        # === 2. EXPERIMENTAL PROPERTIES ===
        print("\n🔄 Importing filtered_properties_v3.csv...")
        df_props = pd.read_csv(EXPERIMENTAL_CSV)
        props_data = df_props.to_dict("records")
        query = """
            UNWIND $rows AS row
            MATCH (m:MOF {refcode: row.`Ref Code`})
            MERGE (p:Property {name: row.Property})
            SET p:Experimental
            MERGE (m)-[r:has_property]->(p)
            SET r.value = row.Value,
                r.units = row.Units,
                r.condition = row.Condition,
                r.summary = row.Summary,
                r.reference = row.Reference
        """
        batch_run(session, query, props_data)
        print("✔ Done filtered_properties_v3.csv")

        # === 3. WATER STABILITY ===
        print("\n🔄 Importing water_stability_filtered.csv...")
        df_water = pd.read_csv(WATER_CSV)
        water_data = df_water.to_dict("records")
        query = """
            UNWIND $rows AS row
            MATCH (m:MOF {refcode: row.`Ref Code`})
            MERGE (p:Property {name: row.Property})
            SET p:Experimental
            MERGE (m)-[r:has_property]->(p)
            SET r.value = row.Value,
                r.units = row.Units,
                r.condition = row.Condition,
                r.summary = row.Summary,
                r.reference = row.Reference
        """
        batch_run(session, query, water_data)
        print("✔ Done water_stability_filtered.csv")

        # === 4. APPLICATIONS ===
        print("\n🔄 Importing applications_filtered_v3.csv...")
        df_app = pd.read_csv(APPLICATIONS_CSV)
        apps_data = df_app.to_dict("records")
        query = """
            UNWIND $rows AS row
            MATCH (m:MOF {refcode: row.`Ref Code`})
            MERGE (a:Application {name: row.Application})
            MERGE (m)-[r:has_application]->(a)
            SET r.recommendation = row.Recommendation,
                r.justification = row.Justification,
                r.source = row.Source
        """
        batch_run(session, query, apps_data)
        print("✔ Done applications_filtered_v3.csv")

        # === 5. SYNTHESIS ===
        print("\n🔄 Importing synthesis_extractions.csv...")
        df_syn = pd.read_csv(SYNTHESIS_CSV)
        syn_data = df_syn.to_dict("records")
        session.run("MERGE (s:Synthesis {name: 'synthesis'})")
        query = """
            UNWIND $rows AS row
            MATCH (m:MOF {refcode: row.`CSD Ref Code`})
            MERGE (s:Synthesis {name: 'synthesis'})
            MERGE (m)-[r:has_synthesis]->(s)
            SET r.metal_precursor = row.`Metal Precursor`,
                r.linker = row.Linker,
                r.solvent = row.Solvent,
                r.temperature = row.Temperature,
                r.reaction_time = row.`Reaction Time`,
                r.synthesis_procedure = row.`Synthesis Procedure`,
                r.additional_conditions = row.`Additional Conditions`,
                r.justification = row.Justification,
                r.reference = row.Reference
        """
        batch_run(session, query, syn_data)
        print("✔ Done synthesis_extractions.csv")

        # === 6. METALS ===
        print("\n🔄 Linking metals from CSD_Info_desc.csv...")
        df_comp = pd.read_csv(CSD_CSV)
        metal_rows = []
        for _, row in df_comp.iterrows():
            refcode = row["CSD code"]
            metals = row.get("Metal types", "")
            if pd.notna(metals):
                for metal in [m.strip() for m in metals.split(",") if m.strip()]:
                    metal_rows.append({"refcode": refcode, "metal": metal})
        query = """
            UNWIND $rows AS row
            MATCH (m:MOF {refcode: row.refcode})
            MERGE (mt:Metal {name: row.metal})
            MERGE (m)-[:has_metal]->(mt)
        """
        batch_run(session, query, metal_rows)
        print("✔ Done linking Metals.")

        # === 7. COMPUTATIONAL ===
        print("\n🔄 Importing computational properties from CSD_Info_desc.csv...")
        for col in df_comp.columns:
            if col == "CSD code":
                continue
            prop_rows = []
            for _, row in df_comp.iterrows():
                val = row[col]
                if pd.notna(val):
                    prop_rows.append({
                        "refcode": row["CSD code"],
                        "property": col,
                        "value": val
                    })
            if prop_rows:
                query = """
                    UNWIND $rows AS row
                    MATCH (m:MOF {refcode: row.refcode})
                    MERGE (p:Property {name: row.property})
                    SET p:Computational
                    MERGE (m)-[r:has_property]->(p)
                    SET r.value = row.value
                """
                batch_run(session, query, prop_rows)

        # === 8. DESCRIPTORS ===
        print("\n🔄 Importing descriptor properties from ChemUnity_all_descriptors.csv...")
        df_desc = pd.read_csv(DESCRIPTOR_CSV)
        df_desc = df_desc[df_desc["name"].notna() & ~df_desc["name"].str.lower().isin(["not provided", "not applicable"])]
        for col in df_desc.columns:
            if col == "name":
                continue
            rows = []
            for _, row in df_desc.iterrows():
                val = row[col]
                if pd.notna(val):
                    rows.append({"refcode": row["name"], "property": col, "value": val})
            if rows:
                query = """
                    UNWIND $rows AS row
                    MATCH (m:MOF {refcode: row.refcode})
                    MERGE (p:Property {name: row.property})
                    SET p:Computational, p:Descriptor
                    MERGE (m)-[r:has_property]->(p)
                    SET r.value = row.value
                """
                batch_run(session, query, rows)

        print("\n📊 AFTER IMPORT:")
        print_graph_stats(session)

if __name__ == "__main__":
    run_queries()
    driver.close()
