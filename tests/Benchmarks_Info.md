# Benchmarks
All workflows presented in this work have been benchmarked. In total, 3 workflows were developed to perform various tasks. The table below summarizes the workflows, benchmark data location, and results

<table width=100%>
  <tr>
    <td width=20%><b>Workflow</b></td>
    <td><b>Extracted Information</b></td>
    <td><b>Benchmark Data</b></td>
    <td width=15%><b>Results</b></td>
  </tr>
  <tr>
    <td>Matching</td>
    <td>MOF names and co-references from each paper</td>
    <td><a href="https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/tests/matching_benchmark/matching_benchmark%20.csv">matching_benchmark.csv</a></td>
    <td>Yield: 98%<br/>Accuracy: 94%</td>
  </tr>
  <tr>
    <td rowspan=2>General Extraction</td>
    <td>Properties associated with a specific MOF</td>
    <td><a href="https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/tests/general_extraction_benchmarks/properties_benchmark.csv">properties_benchmark.csv</a></td>
    <td>Yield: 94%<br/>Precision: 89%</td>
  </tr>
  <tr>
    <td>Synthesis protocol for the specified MOF</td>
    <td><a href="https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/tests/general_extraction_benchmarks/synthesis_benchmark.csv">synthesis_benchmark.csv</a></td>
    <td>Yield: 100%<br/>Precision: 100%</td>
  </tr>
  <tr>
    <td>Specific Property Extraction (CoV)</td>
    <td>Water stability of the specified MOF</td>
    <td><a href="https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/tests/water_stability_benchmark/Water_stability_README.md">more info here</a></td>
    <td>Yield: 100%<br/>Accuracy: 85%</td>
  </tr>
</table>

The benchmark results are generated using the [matching notebook](https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/src/ChemUnity_Matching.ipynb) and the [extraction notebook](https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/src/ChemUnity_Extraction.ipynb).
