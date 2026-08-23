# CSE 572 - Extracting Time Series Properties of Glucose Levels in Artificial Pancreas Project

## Purpose

Project focused on extracting time-series properties from CGM glucose readings for artificial pancreas analysis. The supplied `Result.csv` template indicates the required outputs are percentage-of-time metrics for manual mode and auto mode.

## Files

- `CSE 572_Extracting Time Series Properties of Glucose Levels in Artificial Pancreas Project_Overview Document.pdf` - assignment overview document.
- `CSE 572_Extracting Time Series...Project Files.zip` - supplied data and result template.
- `CSE 572_Template Requirements.docx` - generic README/template instructions for submissions.

## ZIP Contents

`CSE 572_Extracting Time Series...Project Files.zip` contains:

- `Project 1 Student Files New/InsulinData.csv`
- `Project 1 Student Files New/CGMData.csv`
- `Project 1 Student Files New/Result.csv`

Approximate uncompressed sizes:

- `InsulinData.csv` - 4.1 MB
- `CGMData.csv` - 4.3 MB
- `Result.csv` - small output template

## Data Notes

Both CGM and insulin files use Medtronic-style export columns, including:

- `Index`
- `Date`
- `Time`
- `Sensor Glucose (mg/dL)`
- `ISIG Value`
- `Alarm`
- `Suspend`
- `BWZ Carb Input (grams)`
- `Bolus Volume Delivered (U)`
- `Basal Rate (U/h)`

The `Result.csv` template has two rows:

- `Manual Mode`
- `Auto Mode`

Required metric columns include overnight, daytime, and whole-day percentages for:

- hyperglycemia, CGM > 180 mg/dL
- critical hyperglycemia, CGM > 250 mg/dL
- range, CGM >= 70 and <= 180 mg/dL
- secondary range, CGM >= 70 and <= 150 mg/dL
- hypoglycemia level 1, CGM < 70 mg/dL
- hypoglycemia level 2, CGM < 54 mg/dL

## What To Do Next

- Read the overview PDF for exact definitions of overnight/daytime windows and mode segmentation.
- Extract the ZIP before implementation.
- Write code to compute the `Result.csv` metrics from `CGMData.csv` and `InsulinData.csv`.
- Include clear run instructions in the final submission README.

## Notes For Future Codex

- Local PDF text extraction tools were not available when this README was created.
- The included DOCX template is a placeholder requiring steps to execute code, notes, and optional resource links.
