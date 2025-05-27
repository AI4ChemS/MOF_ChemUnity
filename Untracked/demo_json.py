from neo4j import GraphDatabase
from concurrent.futures import ThreadPoolExecutor
import json, os, math

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USER     = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# 🔄 Clean invalid JSON floats
def sanitize_numbers(obj):
    if isinstance(obj, float):
        return None if math.isnan(obj) or math.isinf(obj) else obj
    if isinstance(obj, dict):
        return {k: sanitize_numbers(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_numbers(x) for x in obj]
    return obj

def get_random_refcodes(tx, limit):
    return [
        r["refcode"]
        for r in tx.run("""
            MATCH (m:MOF)
            WITH m ORDER BY rand() LIMIT $limit
            RETURN m.refcode AS refcode
        """, limit=limit)
    ]

def get_mof_data(tx, refcode):
    query = """
    MATCH (m:MOF {refcode: $refcode})

    OPTIONAL MATCH (m)-[:has_name]->(n:MOF_Name)
    WITH m, COLLECT(DISTINCT n.name) AS names

    OPTIONAL MATCH (m)-[:has_source]->(r1:Reference)
    WITH m, names, COLLECT(DISTINCT r1.doi) AS references

    OPTIONAL MATCH (m)-[hp:has_property]->(p:Property:Experimental)
    WITH m, names, references,
         COLLECT(DISTINCT {
             name: p.name, value: hp.value, units: hp.units,
             condition: hp.condition, summary: hp.summary,
             justification: hp.justification, reference: hp.reference
         }) AS experimental_properties

    OPTIONAL MATCH (m)-[hc:has_property]->(cp:Property:Computational)
    WITH m, names, references, experimental_properties,
         COLLECT(DISTINCT {
             name: cp.name, value: hc.value
         }) AS computational_properties

    OPTIONAL MATCH (m)-[hd:has_property]->(dp:Property:Descriptor)
    WITH m, names, references, experimental_properties, computational_properties,
         COLLECT(DISTINCT {
             name: dp.name, value: hd.value
         }) AS descriptors

    OPTIONAL MATCH (m)-[ha:has_application]->(a:Application)
    WITH m, names, references, experimental_properties,
         computational_properties, descriptors,
         COLLECT(DISTINCT {
             name: a.name, recommendation: ha.recommendation,
             justification: ha.justification, reference: ha.reference
         }) AS applications

    OPTIONAL MATCH (m)-[hs:has_synthesis]->(s:Synthesis)
    RETURN m.refcode AS refcode,
           names,
           references,
           experimental_properties,
           computational_properties,
           descriptors,
           applications,
           {
               metal_precursor: hs.metal_precursor,
               linker: hs.linker,
               solvent: hs.solvent,
               temperature: hs.temperature,
               reaction_time: hs.reaction_time,
               procedure: hs.synthesis_procedure,
               conditions: hs.additional_conditions,
               justification: hs.justification,
               reference: hs.reference
           } AS synthesis
    """
    return tx.run(query, refcode=refcode).single().data()

def export_mofs_to_json(limit=50, out_file="mof_demo.json", workers=8):
    with driver.session() as sess:
        refs = sess.read_transaction(get_random_refcodes, limit=limit)

    print(f"🚀 Exporting {limit} MOFs using {workers} threads…")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        raw_data = list(pool.map(lambda r: driver.session().read_transaction(get_mof_data, r), refs))

    clean_data = sanitize_numbers(raw_data)  # 🧼 Make JSON-safe

    with open(out_file, "w") as fh:
        json.dump(clean_data, fh, indent=2, allow_nan=False)  # 💯 spec-compliant
    print(f"✅ JSON export complete: {out_file}")

if __name__ == "__main__":
    export_mofs_to_json(limit=50)
    driver.close()
