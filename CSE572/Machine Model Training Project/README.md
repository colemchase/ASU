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
- Extract nonoverlapping 24-reading no-meal windows beginning two hours after each carbohydrate event. Allow windows to end at the next meal time, with an exclusive right endpoint; do not reserve an extra 30-minute baseline buffer. All carbohydrate events bound these windows, even events excluded as meal candidates. Do not extend beyond insulin/CGM coverage.
- Match readings to a five-minute grid with a 90-second tolerance. Require all 30 meal readings to be observed, finite, and positive; reject any incomplete meal window. For no-meal windows, reject missing endpoints, more than 20% missing values, or more than two consecutive missing readings, and interpolate remaining short interior gaps. Missing timestamps keep their positions instead of compressing the time series.
- Extract the same 24 features from either length: glucose statistics, relative rise/change, peak/trough positions, five-minute derivatives, changes between thirds, normalized Fourier amplitudes, and spectral entropy.
- Train a scaled RBF SVM (`C=1`, default `gamma=scale`). Include the full meal window and 24-point crops beginning at offsets 0, 3, and 6 to address the unspecified alignment of the grader's shorter windows. Weight each original window equally within its class and balance the two classes.
- Split by patient/week before augmentation; remove training windows overlapping validation intervals, including a timing margin. Fit scaling and the classifier within each fold. Report five-fold predictions and separate train-one-patient/test-the-other checks. Finally retrain on both patients.

At prediction time, interpolate partial missing rows and extend the nearest observed endpoint. Entirely missing/nonpositive rows receive the training majority label (0), preserving output row count. Inputs with the wrong number of columns fail clearly. `predict_sample(sample, model=None)` exposes the required single-sample integer prediction function.

## Local results

2,712 usable original windows after removing the no-meal buffer: **757 meal** and **1,955 no meal**.

| Evaluation | Accuracy | Meal F1 | Meal recall |
| --- | ---: | ---: | ---: |
| Grouped five-fold, original 30/24-point windows | 77.6% | 0.684 | 86.8% |
| Same folds, first 24 points of each meal | 75.3% | 0.639 | 78.3% |
| Same folds, last 24 points of each meal | 74.6% | 0.626 | 76.1% |
| Train patient 2, evaluate patient 1 (first 24 points) | 67.3% | 0.542 | 68.7% |
| Train patient 1, evaluate patient 2 (first 24 points) | 68.8% | 0.548 | 68.7% |

Full fold metrics, confusion matrices, extraction counts, and package versions are in `training_report.json`. These are development estimates, not hidden-grader scores. The crop strategy was chosen after observing poor 24-point recall in the initial full-window model, so these checks are not an untouched final test set. Patient holdout results show weaker generalization to an unseen person. The PDF does not specify which 24 points its meal tests retain; both endpoint crops are evaluated here.

Nine regression checks cover close/exactly-two-hour meals, zero carbohydrate entries, missing timestamps, rejection of incomplete meals, constant/variable-length features, overlap purging, strict timestamp boundaries, no-meal windows ending at the next meal, and model loading/prediction in a fresh process (including single-row, empty, missing, and malformed-width inputs).

## SVM versus decision tree comparison

The saved comparison below predates the boundary fix and uses 2,549 windows.
Rerunning the script now uses the corrected extractor and may change its scores.

Run `../../.venv/bin/python compare_models.py` from this directory to reproduce
`model_comparison.json`. This local supporting script is not needed in Ed.

All three configurations use identical extracted windows, features, sample
weights, crop augmentation, and purged patient/week validation folds. Settings
were fixed before this comparison; this is not a hyperparameter search. Scaling
is retained for all models to keep preprocessing consistent, although trees do
not require it. The existing SVM model and submission defaults remain in place.

Results below use the first 24 points of meal validation windows and all 24
points of no-meal windows:

| Model | Accuracy | Meal precision | Meal recall | Meal F1 |
| --- | ---: | ---: | ---: | ---: |
| RBF SVM, C=1 | 76.1% | 58.3% | 80.0% | 0.674 |
| Default decision tree | 65.7% | 46.6% | 73.8% | 0.571 |
| Tree, max depth 5, min leaf size 20 | 71.3% | 52.3% | 82.9% | 0.642 |

The SVM has the highest accuracy and F1 among these configurations. The
constrained tree detects slightly more meals but produces more false positives.
The SVM also leads in accuracy and F1 for the last-24-point evaluation and both
patient holdouts. Its results match the earlier training report exactly.
These results support keeping the SVM for this implementation; they do not
establish that every tuned decision tree would perform worse, or predict the
hidden grader score. All six existing regression checks pass.

## Extraction audit (September 13)

The narrative below records earlier fixes. Current audit artifacts have been
regenerated after buffer removal; class overlap is now expected as noted below.

`../../.venv/bin/python audit_extraction.py` independently parses the raw dates,
checks the meal-event chain rule, traces every accepted value to its source
reading, checks interval bounds and labels, and checks raw-reading overlap across
validation folds. Results are in `extraction_audit.json`; every retained window's
start/end and source timestamp range is in `extraction_window_trace.csv`.
`extraction_audit_before_fix.json` preserves the initial findings.

The audit found a small real bug: nearest timestamp matching could take a reading
just beyond the intended end of a window. Two patient-1 windows were affected
(one meal, one no-meal), with one source reading shared across classes. The
extractor now restricts matching to the requested half-open interval. Both
windows fail the existing missing-endpoint rule and are excluded. A regression
test uses a two-second clock drift to reproduce this case. The corrected audit
finds no out-of-interval values, shared readings across classes, or shared
readings between training and validation. All seven regression checks pass.

Other findings:

- All raw timestamps parse consistently with independent explicit-format parsing,
  including patient 2 dates that already contain a midnight timestamp.
- The later-meal rule matches an independent forward event-chain calculation.
  The data has 163 gaps shorter than two hours, but no exactly-two-hour gaps;
  the exact case is covered by synthetic regression tests.
- The extra 30-minute buffer before the next meal excludes 197 otherwise usable
  no-meal windows. This is a conservative design choice, not required by the PDF.
- The missing-meal correction now excludes all 32 meal windows that previously
  needed interpolation. Every retained meal and its training crops contain only
  observed readings. Short-gap interpolation remains available for no-meal data.
- The grader's 24-value meal-window alignment remains unspecified. An audit of
  the supplied training records cannot establish the hidden test convention.

The model was retrained locally after the fix. Removing two windows also changes
the stratified group fold assignments, so metric differences are not a controlled
estimate of the fix's performance effect. No new submission was made. This small
bug does not establish the cause of the hidden-test accuracy gap.

## Missing meal readings correction

Training now rejects a 30-reading meal window if any reading is missing,
nonfinite, or nonpositive, including missing timestamps. This implements the
assignment's option of dropping incomplete windows using a zero-missing-value
threshold for meals. It avoids inventing a meal-response shape through
interpolation, at the cost of 32 fewer meal examples. Eight regression checks
pass, including missing/invalid meal rejection and retention of complete meals.
The full audit confirms zero retained meals need interpolation.

The change is limited to labeled training meals. Test inputs have unknown labels
and must each receive a prediction; their existing missing-value fallback remains
in place. The no-meal buffer and model settings are unchanged. The local model
and reports have been regenerated; no Ed submission was made. Changes in sample
counts also affect fold assignments, so the updated scores are not a controlled
measure of improvement from this correction alone.

## Polynomial and KNN meal-imputation experiment

These saved experiment scores predate no-meal buffer removal.

Run `../../.venv/bin/python compare_imputation.py` to generate
`imputation_comparison.json`. This experiment changes handling of the 32
incomplete training meal windows only. No-meal interpolation, extraction
boundaries, feature definitions, SVM settings, and test-time behavior stay fixed.
The submission model and default complete-meal requirement are unchanged.

A common candidate pool defines five purged patient/week folds. Every method is
evaluated on exactly the same 2,515 windows (complete meals plus accepted no-meal
windows). Incomplete validation meals are excluded for every method. The drop
baseline excludes incomplete training meals; the other methods retain and fill
them. Consequently these scores are comparable with each other, but not directly
with older reports using different fold assignments.

| Handling of incomplete training meals | First-24 accuracy | Meal F1 | Meal recall |
| --- | ---: | ---: | ---: |
| Drop | 76.22% | 0.6721 | 80.98% |
| Linear interpolation | 76.10% | 0.6707 | 80.85% |
| Quadratic regression | 75.98% | 0.6703 | 81.11% |
| KNN imputation | 76.02% | 0.6703 | 80.98% |

Quadratic regression fits a degree-two curve to each window's observed readings,
fills only missing positions, and clips estimates to that window's observed
range. KNN uses five distance-weighted neighboring 30-point training meals;
its donor pool is fitted separately within each training fold. Both operate
before crop augmentation. No validation windows enter the donor pool. These are
fixed configurations rather than a search over polynomial degrees or K values.

The drop baseline also has the best first-24 accuracy/F1 in both patient holdouts.
Last-24 results are mixed: linear interpolation has F1 0.6522, quadratic 0.6512,
drop 0.6499, and KNN 0.6496. Differences are small and do not establish a robust
winner across all possible settings or hidden tests.

A separate diagnostic masks one or two consecutive internal readings in each
complete validation meal (1,159 masked points total). Mean absolute reconstruction
error is 2.87 mg/dL for linear interpolation, 12.48 for quadratic regression,
and 10.65 for KNN. These synthetic gaps may not represent real missingness and
are not a hidden-test score. The diagnostic shows that more complex filling is
not automatically better for these short gaps.

All eight existing regression checks passed. Additional execution checks verified
exact reconstruction of a known quadratic, preservation of observed values,
training-only KNN donors, invariance to changes in held-out rows, and the drop
policy. No new Ed submission was made.

## Removal of the extra no-meal buffer

No-meal windows now extend up to the next meal's timestamp, excluding that
endpoint. For example, meals at 09:00 and 13:00 permit a no-meal window from
11:00 to 13:00; a new meal at 12:59:59 invalidates that window. The regression
suite verifies both cases. This recovers 197 no-meal windows, for 1,955 total.
The complete-meal policy remains unchanged at 757 retained meal windows.

No-meal readings can now also belong to the next meal window's pre-meal baseline.
That overlap is permitted by the extraction intervals; it is distinct from the
previous bug that included readings outside an interval. Validation still purges
overlapping training windows, and the updated source audit confirms zero shared
readings between training and validation and zero interval violations. All nine
regression tests pass. The local model and training report were regenerated.

The larger dataset changes class counts and fold assignments. Updated validation
scores should not be treated as a controlled estimate of the change's effect, or
as hidden-grader results. Nothing has been resubmitted to Ed.

## Latest feedback review and SVM tuning

`requirements_review.md` maps the pasted Ed instructions to implementation and
verification. The latest supplied hidden result is 198/200, accuracy 62.77%, F1
0.6884. The remaining grader complaint identifies wrong predictions but does not
provide their rows or labels. Passing the local checks does not establish that
all hidden predictions are correct.

Training now supports optional nested tuning:

```sh
python3 train.py --tune --report tuning_report.json
```

This searches eight fixed SVM configurations using three inner purged group folds
and evaluates the selection procedure on five outer folds. It includes C=1/10,
gamma=scale/0.01, and meal penalty multipliers 1/0.7. Selection scores average
meal F1 across first/last 24-point views. Preprocessing and augmentation remain
inside the training folds. The default `python3 train.py` retains the existing
model settings and runtime; tuning is optional.

| Evaluation | Current accuracy | Nested tuning accuracy | Current F1 | Nested tuning F1 |
| --- | ---: | ---: | ---: | ---: |
| First 24 readings | 75.26% | 75.22% | 0.6387 | 0.6383 |
| Last 24 readings | 74.63% | 74.56% | 0.6261 | 0.6250 |

Selection on the full training dataset chose C=1, gamma=scale, and multiplier=1,
equivalent to the current settings. No improvement was demonstrated; the current
model.pkl was retained. Full results are in tuning_report.json. The selected
candidate also produced identical predictions to the current model on 200 varied
synthetic rows, including partially and fully missing rows; a fresh-process CSV
prediction check passed. Nine regression checks and the source audit also pass.
No new Ed submission was made, and 200/200 is not guaranteed.

## Crop and shape-feature experiments

The latest pasted hidden score is 198/200, accuracy 63.64%, F1 0.6957. The exact
Ed source/model revision is not available locally, so a score change cannot be
attributed to a local code revision with certainty.

`compare_representation.py` compares baseline augmentation, three 24-point
crops only, all seven 24-point crops, removal of absolute mean glucose, and
fold-fitted selection of 12 features. Results in `representation_comparison.json`
show no clear improvement over the baseline across alignments and patients.

`compare_shape_features.py` adds 14 features describing 15/30/60-minute changes,
early/late slopes, sustained rising/falling runs, and peak timing. The standard
SVM with these features improves first-24 accuracy from 75.26% to 75.77% and F1
from 0.6387 to 0.6408. Accuracy increases for both patient holdouts, but F1 is
mixed across patients and crop alignments. The same features with gamma=0.01
do not show a clear overall advantage. Details are in `shape_comparison.json`.
These are repeated development comparisons, not untouched-test estimates.

The baseline files/model remain the default. A separately trained, self-contained
experimental pair is in `candidates/shape/train.py` and `candidates/shape/test.py`.
Use both together and retrain because this candidate has 38 features and a new
pickle schema. Its README has execution instructions and limitations. No hidden
score improvement is claimed for this candidate and no submission was made.
