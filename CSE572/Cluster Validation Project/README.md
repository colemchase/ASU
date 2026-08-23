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

## What To Do Next

- Read the overview PDF for exact feature extraction rules, clustering algorithms, validation metrics, and required output format.
- Extract the ZIP before implementation.
- Expect to handle missing glucose values and align insulin events with CGM time windows.
- Likely validation metrics may include SSE, entropy, purity, or similar cluster-quality measures, but verify this in the PDF.

## Notes For Future Codex

- No implementation files are present yet.
- Local PDF text extraction tools were not available when this README was created, so exact rubric details must be checked in the PDF.
