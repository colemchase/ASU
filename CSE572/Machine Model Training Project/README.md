# CSE 572 — Machine Model Training Project

Classify CGM time series as **meal (1)** or **no meal (0)** using both supplied patients. The overview PDF is the assignment authority. It requires `train.py`, `test.py`, a pickled model, five-fold evaluation, and a headerless `Result.csv` containing one prediction per input row.

## Run locally

From this project directory, using the repository virtual environment:

```sh
../../.venv/bin/python train.py
../../.venv/bin/python test.py
../../.venv/bin/python verify_project.py
```

Training writes `model.pkl` and `training_report.json`. Prediction requires the grader's **headerless N × 24 `test.csv`**, with glucose values ordered chronologically, and writes **N × 1 `Result.csv`** without a header or index. The supplied ZIP does not include `test.csv`; validation uses temporary inputs and does not create a fake grader result.

For a fresh environment, use Python 3.14 and install `requirements.txt`. The PDF specifies Python 3.14.5; local verification used 3.14.6 with the exact specified NumPy, pandas, SciPy, and scikit-learn versions. Retrain in the grading environment to produce its own compatible pickle.

```sh
python3 -m pip install -r requirements.txt
unzip -j "CSE 572_Machine Model Training Project Files.zip" '*.csv' -d .
python3 train.py
python3 test.py
```

Both scripts default to files in the execution directory and accept optional paths:

```sh
python3 train.py --data-dir . --model model.pkl --report training_report.json
python3 test.py --input test.csv --model model.pkl --output Result.csv
```

## Submission

Copy **both `train.py` and `test.py`** into the corresponding Ed Lessons files. Training imports feature extraction from `test.py`; neither file executes its main function on import. No third source file is needed. Run `python3 train.py`, then `python3 test.py` with the workspace data. Use Ed's Test and Submit controls as directed by the assignment. This local implementation has not been submitted to Ed.

`verify_project.py`, `requirements.txt`, and `training_report.json` are local supporting files. Extracted datasets, the generated pickle, and local input/output CSVs are ignored by Git; the supplied archive remains the source for the datasets.

## Extraction and modeling

- Parse both date formats, select columns by name (ignoring patient 2's extra index), sort chronologically, and average duplicate CGM timestamps.
- A nonmissing, nonzero carbohydrate entry identifies a meal. If another meal occurs within **or exactly at** two hours, discard the earlier candidate and use the later event. This also handles chains of close meals without duplicate windows.
- Extract 30 readings from the first CGM sample at/after `meal time − 30 minutes`, representing a half-open 150-minute interval.
- Extract nonoverlapping 24-reading no-meal windows beginning two hours after each carbohydrate event. Stop before the next meal's 30-minute baseline, conservatively excluding shared baseline data. All carbohydrate events bound these windows, even events excluded as meal candidates. Do not extend beyond insulin/CGM coverage.
- Match readings to a five-minute grid with a 90-second tolerance. Reject training windows with missing endpoints, more than 20% missing values, or more than two consecutive missing readings. Interpolate remaining short interior gaps. Missing timestamps keep their positions instead of compressing the time series.
- Extract the same 24 features from either length: glucose statistics, relative rise/change, peak/trough positions, five-minute derivatives, changes between thirds, normalized Fourier amplitudes, and spectral entropy.
- Train a scaled RBF SVM (`C=1`, default `gamma=scale`). Include the full meal window and 24-point crops beginning at offsets 0, 3, and 6 to address the unspecified alignment of the grader's shorter windows. Weight each original window equally within its class and balance the two classes.
- Split by patient/week before augmentation; remove training windows overlapping validation intervals, including a timing margin. Fit scaling and the classifier within each fold. Report five-fold predictions and separate train-one-patient/test-the-other checks. Finally retrain on both patients.

At prediction time, interpolate partial missing rows and extend the nearest observed endpoint. Entirely missing/nonpositive rows receive the training majority label (0), preserving output row count. Inputs with the wrong number of columns fail clearly. `predict_sample(sample, model=None)` exposes the required single-sample integer prediction function.

## Local results

2,549 usable original windows: **790 meal** and **1,759 no meal**.

| Evaluation | Accuracy | Meal F1 | Meal recall |
| --- | ---: | ---: | ---: |
| Grouped five-fold, original 30/24-point windows | 78.2% | 0.712 | 86.8% |
| Same folds, first 24 points of each meal | 76.1% | 0.674 | 80.0% |
| Same folds, last 24 points of each meal | 75.3% | 0.661 | 77.6% |
| Train patient 2, evaluate patient 1 (first 24 points) | 67.7% | 0.566 | 67.5% |
| Train patient 1, evaluate patient 2 (first 24 points) | 69.5% | 0.581 | 69.1% |

Full fold metrics, confusion matrices, extraction counts, and package versions are in `training_report.json`. These are development estimates, not hidden-grader scores. The crop strategy was chosen after observing poor 24-point recall in the initial full-window model, so these checks are not an untouched final test set. Patient holdout results show weaker generalization to an unseen person. The PDF does not specify which 24 points its meal tests retain; both endpoint crops are evaluated here.

Six regression checks cover close/exactly-two-hour meals, zero carbohydrate entries, missing timestamps, constant/variable-length features, overlap purging, and model loading/prediction in a fresh process (including single-row, empty, missing, and malformed-width inputs).
