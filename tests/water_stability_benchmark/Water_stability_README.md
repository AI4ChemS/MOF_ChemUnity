# Water Stability Extraction Benchmark
### Ground Truth Data
The ground truth benchmark data for water stability extraction is adapted from [Ansari et al. 2024](https://pubs.rsc.org/en/content/articlehtml/2024/dd/d4dd00252k) Case 3 study [(found here)](https://github.com/AI4ChemS/Eunomia/tree/main/data). Their data contains MOF names and associated true water stability label (Stable, Unstable, Not Provided).

### Extraction Methodology
In this work, Chain-of-Verification (CoV) from Ansari et al. 2024 is implemented with minor modifications. Additionally, since the named entity recognition and co-reference resolution were tackled in the matching workflow, the MOF name from the ground truth is provided to the CoV. 

<p align="center">
  <img width="490" alt="CoV_V2" src="https://github.com/user-attachments/assets/0804f5c0-8616-490f-81e2-582c4ec784b2" />
</p>

The extraction methodology for water stability is also shown in this [notebook](https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/src/ChemUnity_Extraction.ipynb).

### Benchmark Results
The results from the extraction can be found [here](https://github.com/AI4ChemS/MOF_ChemUnity/tree/main/tests/water_stability_benchmark/eunomia_edit5.csv). Additionally, the confusion matrix below shows that our implementation of CoV acheives similar performance to Ansari et al. 2024. 

<p align="center">
  <img width="490" alt="New_eunomia_benchmark" src="https://github.com/user-attachments/assets/3ef71ee8-cabf-4b98-b6c4-458ab689e279" />
</p>
