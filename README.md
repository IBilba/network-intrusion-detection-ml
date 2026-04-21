# Network Intrusion Detection — CIC-IDS-2017

Lab project for **Data Mining and Learning Algorithms**, Spring 2025-2026,
University of Patras (Dept. of Computer Engineering & Informatics).

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
python -m ipykernel install --user --name nids --display-name "Python (nids)"
```

## Getting the data

Download the CIC-IDS-2017 MachineLearningCSV.zip from
<https://www.kaggle.com/datasets/chethuhn/network-intrusion-dataset/> (or
the official UNB mirror) and extract the 8 CSV files into `./data/`.

After extraction, `./data/` should contain files such as:

```
Monday-WorkingHours.pcap_ISCX.csv
Tuesday-WorkingHours.pcap_ISCX.csv
Wednesday-workingHours.pcap_ISCX.csv
Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
Friday-WorkingHours-Morning.pcap_ISCX.csv
Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
```

## Running the notebooks

Open each notebook in order — they depend on artifacts saved by the
previous one:

1. `notebooks/q1_eda.ipynb`        — EDA, cleaning, feature selection
2. `notebooks/q2_classification.ipynb` — supervised models
3. `notebooks/q3_clustering.ipynb` — unsupervised models

## Layout

```
data/                raw CSVs (gitignored)
notebooks/           Q1/Q2/Q3 analysis notebooks
utils/helpers.py     shared loading & cleaning helpers
outputs/figures/     saved plots (PNG)
outputs/results/     saved metrics tables (CSV)
report/              final PDF report assets
requirements.txt     pinned library list
```

## Reproducibility

`utils.helpers.RANDOM_STATE = 42` is used for every split, model seed,
and stochastic operation. Re-running any notebook top-to-bottom gives
identical results.
