# Experimental glucose-shape candidate

This candidate adds 14 features to the baseline's 24: changes over 15/30/60
minutes, early/late slopes, sustained-rise/fall lengths, lag-one correlation,
and excursion timing. It uses the same extraction, complete-meal requirement,
SVM, weighting, and crop augmentation as the current submission.

Copy BOTH train.py and test.py from this directory into Ed, and run training
before prediction. Its pickle uses a different feature schema from the baseline.
The two source files are self-contained; no experiment script is required.

From this directory for local reproduction:

```sh
../../../../.venv/bin/python train.py --data-dir ../..
../../../../.venv/bin/python test.py --input /path/to/test.csv
```

Development results show a small accuracy improvement, not a demonstrated
hidden-test improvement. First-24 accuracy/F1: 75.77%/0.6408 versus baseline
75.26%/0.6387. Last-24 F1 decreased from 0.6261 to 0.6242; middle-crop F1 is
nearly unchanged. Both patient-holdout accuracies increased, while F1 improved
for one patient and decreased slightly for the other. Repeated development
comparisons increase selection optimism. No 200/200 or perfect predictions
are promised, and this candidate has not been submitted by the assistant.

## SVM tuning results

The expanded search tried 24 fixed combinations: C in {0.3, 1, 3, 10}, gamma in
{scale, 0.01}, and an additional meal penalty multiplier in {1, 0.7, 1.3}.
The existing original-window class balancing and crop weights remain in effect.
Selection uses three inner purged patient/week folds, maximizing mean meal F1
across first/last 24-point views. Five outer folds evaluate this selection
procedure; patient holdouts select using only the training patient. No hidden
labels enter the search. The report is `tuning_report.json`.

| Evaluation | Untuned accuracy | Nested tuning accuracy | Untuned F1 | Nested tuning F1 |
| --- | ---: | ---: | ---: | ---: |
| First 24 readings | 75.77% | 75.15% | 0.6408 | 0.6357 |
| Last 24 readings | 74.96% | 74.59% | 0.6242 | 0.6245 |
| Patient 1 holdout | 68.77% | 66.20% | 0.5392 | 0.5418 |
| Patient 2 holdout | 69.24% | 67.01% | 0.5569 | 0.5612 |

Selection using all training data chose C=3, gamma=scale, and meal multiplier=1.3.
The final model is saved separately as `model_tuned.pkl`. Its stronger meal
penalty trades accuracy for meal detection in the holdout checks. There is no
clear overall improvement, so `model.pkl` and default training remain untuned.
The nested metrics evaluate the selection procedure, not an independent test of
that final full-data parameter choice. All nine regression tests pass. Additional
checks confirm tuned pickle loading, single/batch prediction agreement, and
headerless binary output for 200 inputs in a fresh process.

To reproduce tuning locally from this directory:

```sh
../../../../.venv/bin/python train.py --data-dir ../.. --tune --model model_tuned.pkl --report tuning_report.json
../../../../.venv/bin/python test.py --model model_tuned.pkl --input /path/to/test.csv
```

In Ed, `python3 train.py --tune` would write the selected model to the default
`model.pkl`, followed by `python3 test.py`. This is an optional experiment, not
a recommendation to replace the untuned model. No Ed submission was made.
