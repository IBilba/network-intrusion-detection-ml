# Network Intrusion Detection — CIC-IDS-2017

Lab project for **Data Mining and Learning Algorithms**, Spring 2025-2026,
University of Patras (Dept. of Computer Engineering & Informatics).

End-to-end ML pipeline on the CIC-IDS-2017 dataset:

- **Q1 — EDA, cleaning, feature selection** (✅ complete)
- **Q2 — Classification** (Logistic Regression, Decision Tree, Random Forest, with split- and CV-based grid search)
- **Q3 — Clustering** (K-Means, Hierarchical, DBSCAN, with PCA visualization)

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

Requires Python 3.10+ and ~16 GB RAM (the full load uses ~4-6 GB after memory optimization).

## Getting the data

Download the CIC-IDS-2017 MachineLearningCSV.zip from
<https://www.kaggle.com/datasets/chethuhn/network-intrusion-dataset/> (or
the official UNB mirror) and extract the 8 CSV files into `./data/`.

After extraction, `./data/` should contain:

```text
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
previous one (Q1 produces `data/cic_ids_2017_clean.parquet`, which Q2/Q3 load directly):

1. `notebooks/q1_eda.ipynb`            — EDA, cleaning, feature selection
2. `notebooks/q2_classification.ipynb` — supervised models (LR / DT / RF)
3. `notebooks/q3_clustering.ipynb`     — unsupervised models (K-Means / Hierarchical / DBSCAN)

To execute a notebook headlessly:

```bash
jupyter nbconvert --to notebook --execute notebooks/q1_eda.ipynb --output q1_eda.ipynb
```

## Layout

```text
data/                raw CSVs (gitignored) + cleaned Parquet snapshot
notebooks/           Q1/Q2/Q3 analysis notebooks
utils/
  __init__.py        re-exports the public helper API
  helpers.py         loading, cleaning, caching, plotting helpers
scripts/             auxiliary build/automation scripts
outputs/
  figures/           saved plots (PNG)
  results/           saved metrics tables (CSV)
report/
  doc.tex            full LaTeX report (compile with XeLaTeX)
  exam_notes.md      oral-exam prep notes (Greek + English terms)
exercise.pdf         official assignment brief
prompt.md            project specification / teaching contract
requirements.txt     pinned library list
```

## Reproducibility

`utils.RANDOM_STATE = 42` is used for every split, model seed, and
stochastic operation (sampling, shuffling, K-Means init, RF bootstrap,
GridSearchCV folds). Re-running any notebook top-to-bottom yields
bit-identical results.
