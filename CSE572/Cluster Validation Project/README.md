# CSE 572 - Cluster Validation Project

## Purpose

Clustering and cluster validation project using CGM and insulin data. This appears to build on the artificial pancreas datasets and likely requires extracting meal/no-meal or glucose-response features, clustering them, and evaluating cluster quality.

## Files

- `CSE 572_Cluster Validation Project_Overview Document.pdf` - assignment overview document.
- `CSE 572_Cluster Validation Project Files.zip` - supplied datasets.

## ZIP Contents

`CSE 572_Cluster Validation Project Files.zip` contains:

- `Project 3 Files/CGMData.csv`
- `Project 3 Files/InsulinData.csv`

Approximate uncompressed sizes:

- `CGMData.csv` - 4.3 MB
- `InsulinData.csv` - 4.1 MB

## Data Notes

The CSVs use the same Medtronic-style export format as the earlier CSE 572 projects. Important columns likely include:

- `Date`
- `Time`
- `Sensor Glucose (mg/dL)`
- `BWZ Carb Input (grams)`
- `Bolus Volume Delivered (U)`
- `Basal Rate (U/h)`
- `Alarm`
- `Suspend`

## Current Implementation

`main.py` prefers Ed's `CGMData.csv` and `InsulinData.csv` files, and falls
back to the supplied ZIP only for local use. It:

1. selects carbohydrate meal events that have no following meal within two hours;
2. aligns 30 five-minute CGM readings beginning 30 minutes before each meal;
3. transforms each complete 30-point meal window into the same 24 engineered
   features used by the Project 2 implementation, then standardizes them;
4. derives the required number of 20-gram bins from the full insulin export,
   then trains KMeans using that number;
5. grid-searches DBSCAN's `eps` and `min_samples`, retaining only settings
   that form that same number of non-noise clusters and preferring fewer noise
   points; and
6. writes the required headerless six-value `Result.csv`, plus an inspectable `dbscan_grid.csv`.

Run it after installing the pinned packages:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

This implementation is self-contained: it retains Project 2's 24-feature
schema in `main.py` so the assignment can be run without importing another
project directory. The carbohydrate amount for each meal is held back from
clustering and used only to form ground-truth bins for entropy and purity.
