# Review of the latest Ed feedback

The latest supplied feedback reports **198/200**, meal F1 **0.6884057971**,
accuracy **0.6277056277**, and **0/1 passed**. It says some output values are
incorrect but supplies no input rows, expected labels, confusion matrix, or
performance-to-points formula. The meaning of its reference means and standard
deviations is not specified. Therefore individual hidden errors cannot be
identified or certified fixed locally.

| Requirement | Implementation and verification |
| --- | --- |
| Read both patients' CGM and insulin files | Read by column name; independent explicit-format timestamp audit agrees with the training parser. |
| Detect nonmissing, nonzero carbohydrate entries | Used as meal events; zero values do not interrupt no-meal periods. |
| Shift to the later meal for gaps <=2 hours | Forward-chain audit and close/exactly-two-hour regression checks. |
| Extract 30-reading meal windows | Strict timestamp interval from meal minus 30 minutes; reject missing or invalid meal readings. |
| Extract 24-reading no-meal windows after meal plus 2 hours | No extra baseline buffer; next meal is the exclusive endpoint. Check a meal exactly at, and one second before, that endpoint. |
| Handle missing data | Drop incomplete meals; bounded short-gap interpolation for no-meal training rows. This is a chosen policy, not the only permissible one. |
| Equal feature-vector lengths | 24 features for both input lengths; same feature function in training and prediction. |
| Train a classifier and save with pickle | Scaled, weighted RBF SVM saved in model.pkl. |
| k-fold evaluation | Five patient/week folds; purge shared source intervals; scale and augment within each training fold. |
| Predict a single sample | predict_sample returns an integer 0 or 1. |
| Read N x 24 test.csv and write N x 1 Result.csv | Fresh-process checks verify one label per row, no header/index, single-row input, missing values, and invalid widths. |
| Keep train.py/test.py and use execution-directory paths | Both files run with their required names; no third submission source file needed. |

Nine regression checks and the full source-timestamp audit pass. Meal/no-meal
windows may share pre-meal baseline readings as the specified intervals allow;
training and validation share none after purging. The date/midnight and
five-subject/two-subject wording do not supply additional datasets: the named
four files provide two patients. The 24-reading test meal alignment remains
unspecified. We evaluate first and last crops and do not infer hidden labels.

The new --tune option evaluates eight fixed combinations of C (1 or 10), gamma
(scale or 0.01), and meal penalty multiplier (1 or 0.7). Three inner purged
patient/week folds select by mean meal F1 across first/last 24-reading crops;
five outer folds evaluate that selection procedure. Patient holdouts also select
using only the training patient. The same candidate grid is selected on all
available training data before writing the final tuned artifact.

Aggregate hidden scores cannot guarantee perfect predictions or 200/200. This
review does not claim the grader's failing prediction check has been resolved.
No Ed submission is performed by the local scripts.
