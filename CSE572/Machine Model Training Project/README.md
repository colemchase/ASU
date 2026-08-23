# CSE 572 - Machine Model Training Project

## Purpose

Machine learning project using CGM and insulin data. Based on the supplied files, this likely trains a model on one patient's CGM/insulin data and evaluates or applies it to a second patient's data.

## Files

- `CSE 572_Machine Model Training Project_Overview Document.pdf` - assignment overview document.
- `CSE 572_Machine Model Training Project Files.zip` - supplied datasets.

## ZIP Contents

`CSE 572_Machine Model Training Project Files.zip` contains:

- `CGMData.csv` - first patient/source CGM data
- `InsulinData.csv` - first patient/source insulin data
- `CGM_patient2.csv` - second patient CGM data
- `Insulin_patient2.csv` - second patient insulin data

Approximate uncompressed sizes:

- `CGMData.csv` - 4.3 MB
- `InsulinData.csv` - 4.1 MB
- `CGM_patient2.csv` - 2.9 MB
- `Insulin_patient2.csv` - 2.6 MB

## Data Notes

The CSVs include CGM readings and insulin pump fields. Important columns likely include:

- `Date`
- `Time`
- `Sensor Glucose (mg/dL)`
- `ISIG Value`
- `BWZ Carb Input (grams)`
- `Bolus Volume Delivered (U)`
- `Basal Rate (U/h)`
- `Alarm`
- `Suspend`

The patient 2 CSVs include an extra leading unnamed index column before `Index`.

## What To Do Next

- Read the overview PDF for the exact prediction/classification target, feature requirements, model choices, and expected output files.
- Extract the ZIP before implementation.
- Normalize timestamp parsing across both patient datasets.
- Watch for missing `Sensor Glucose (mg/dL)` values and non-numeric blanks.

## Notes For Future Codex

- No implementation files are present yet.
- Local PDF text extraction tools were not available when this README was created, so exact model/rubric details must be checked in the PDF.
