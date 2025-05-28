from neo4j import GraphDatabase
import pandas as pd
from dotenv import load_dotenv
import os

# ========== CONFIG ==========
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# ========== FILE PATHS ==========
MATCHING_CSV = "src/Examples/KG_Data/matching.csv"
EXPERIMENTAL_CSV = "src/Examples/KG_Data/filtered_experimental_properties.csv"
WATER_CSV = "src/Examples/KG_Data/water_stability.csv"
APPLICATIONS_CSV = "src/Examples/KG_Data/applications.csv"
SYNTHESIS_CSV = "src/Examples/KG_Data/synthesis.csv"
DESCRIPTOR_CSV = "src/Examples/KG_Data/descriptors.csv"
COMP_PROP_CSV = "src/Examples/KG_Data/computational_properties.csv"

# ========== SETUP ==========
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
valid_refcodes = set(pd.read_csv(MATCHING_CSV)["CSD Ref Code"].dropna().unique())

def batch_run(session, query, rows, batch_size=1000):
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        session.run(query, {"rows": batch})

def create_indexes(session):
    queries = [
        "CREATE INDEX IF NOT EXISTS FOR (m:MOF) ON (m.refcode)",
        "CREATE INDEX IF NOT EXISTS FOR (r:Reference) ON (r.doi)",
        "CREATE INDEX IF NOT EXISTS FOR (n:MOF_Name) ON (n.name)",
        "CREATE INDEX IF NOT EXISTS FOR (p:Property) ON (p.name)",
        "CREATE INDEX IF NOT EXISTS FOR (a:Application) ON (a.name)"
    ]
    for q in queries:
        session.run(q)

def import_matching(session):
    print("🔄 Importing matching.csv...")
    df = pd.read_csv(MATCHING_CSV)
    rows = []
    for _, row in df.iterrows():
        names = str(row["MOF Name"]).split("<|>")
        refcode = row["CSD Ref Code"]
        doi = row["DOI"]
        if str(refcode).lower() in ["not provided", "not applicable"]:
            continue
        for name in names:
            if name.lower().strip() in ["not provided", "not applicable"]:
                continue
            rows.append({"refcode": refcode.strip(), "doi": doi, "name": name.strip()})
    query = """
        UNWIND $rows AS row
        MERGE (m:MOF {refcode: row.refcode})
        MERGE (r:Reference {doi: row.doi})
        MERGE (n:MOF_Name {name: row.name})
        MERGE (m)-[:has_name]->(n)
        MERGE (m)-[:has_source]->(r)
        MERGE (n)-[:has_source]->(r)
    """
    batch_run(session, query, rows)

def import_experimental_properties(session, csv_path):
    print(f"🔄 Importing experimental props from {csv_path}...")
    df = pd.read_csv(csv_path)
    if "Justification" not in df.columns and "Summary" in df.columns:
        df["Justification"] = df["Summary"]
    rows = df.to_dict("records")
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
            r.justification = row.Justification,
            r.reference = row.Reference
    """
    batch_run(session, query, rows)

def import_applications(session):
    print("🔄 Importing applications.csv...")
    df = pd.read_csv(APPLICATIONS_CSV)
    if "Reference" not in df.columns and "Source" in df.columns:
        df["Reference"] = df["Source"]
    rows = df.to_dict("records")
    query = """
        UNWIND $rows AS row
        MATCH (m:MOF {refcode: row.`Ref Code`})
        MERGE (a:Application {name: row.Application})
        MERGE (m)-[r:has_application]->(a)
        SET r.recommendation = row.Recommendation,
            r.justification = row.Justification,
            r.reference = row.Reference
    """
    batch_run(session, query, rows)

def import_synthesis(session):
    print("🔄 Importing synthesis.csv...")
    df = pd.read_csv(SYNTHESIS_CSV)
    rows = df.to_dict("records")
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
    batch_run(session, query, rows)

def import_computational_properties(session, csv_path, add_descriptor_label=False):
    label = ":Computational" + (":Descriptor" if add_descriptor_label else "")
    label_text = 'descriptors' if add_descriptor_label else 'computational properties'
    print(f"🔄 Importing {label_text} from {csv_path}...")

    df = pd.read_csv(csv_path)

    if add_descriptor_label:
        ref_col = "name"
        df = df[df[ref_col].notna() & ~df[ref_col].str.lower().isin(["not provided", "not applicable"])]
    else:
        ref_col = "CSD code"

    for col in df.columns:
        if col == ref_col:
            continue
        rows = []
        for _, row in df.iterrows():
            ref = row[ref_col]
            if ref not in valid_refcodes:
                continue
            val = row[col]
            if pd.notna(val):
                rows.append({
                    "refcode": ref,
                    "property": col,
                    "value": val
                })
        if rows:
            query = f"""
                UNWIND $rows AS row
                MATCH (m:MOF {{refcode: row.refcode}})
                MERGE (p:Property {{name: row.property}})
                SET p{label}
                MERGE (m)-[r:has_property]->(p)
                SET r.value = row.value
            """
            batch_run(session, query, rows)

def print_graph_stats(session):
    for label in ["MOF", "Property", "Application", "Reference", "MOF_Name"]:
        count = session.run(f"MATCH (n:{label}) RETURN count(n) AS count").single()["count"]
        print(f"   {label}s: {count}")

# ========== RUN ==========
def run_all():
    with driver.session() as session:
        create_indexes(session)
        print("\n📊 BEFORE IMPORT:")
        print_graph_stats(session)

        import_matching(session)
        import_experimental_properties(session, EXPERIMENTAL_CSV)
        import_experimental_properties(session, WATER_CSV)
        import_applications(session)
        import_synthesis(session)
        import_computational_properties(session, COMP_PROP_CSV)
        import_computational_properties(session, DESCRIPTOR_CSV, add_descriptor_label=True)

        print("\n📊 AFTER IMPORT:")
        print_graph_stats(session)

if __name__ == "__main__":
    run_all()
    driver.close()
