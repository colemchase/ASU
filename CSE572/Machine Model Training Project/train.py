"""Extract both patients' CGM windows, cross-validate an SVM, and save it."""
import argparse
import json
import pickle
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.base import clone
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from test import FEATURE_NAMES, FEATURE_VERSION, MODEL_PATH, extract_features

GLUCOSE = "Sensor Glucose (mg/dL)"
CARBS = "BWZ Carb Input (grams)"
PATIENT_FILES = [
    ("CGMData.csv", "InsulinData.csv"),
    ("CGM_patient2.csv", "Insulin_patient2.csv"),
]
FIVE_MINUTES = pd.Timedelta(minutes=5)
TWO_HOURS = pd.Timedelta(hours=2)
HALF_HOUR = pd.Timedelta(minutes=30)


def read_export(path, value_column):
    frame = pd.read_csv(path, usecols=["Date", "Time", value_column])
    timestamp = pd.to_datetime(
        frame["Date"] + " " + frame["Time"], format="mixed", errors="coerce"
    )
    values = pd.to_numeric(frame[value_column], errors="coerce")
    series = pd.Series(values.to_numpy(), index=pd.DatetimeIndex(timestamp))
    series = series[series.index.notna()]
    return series.sort_index()


def meal_starts(insulin):
    """Keep the last event in a chain with gaps <= two hours (PDF cases b/c)."""
    events = insulin[insulin.notna() & insulin.ne(0)].index.unique().sort_values()
    valid = [
        time for i, time in enumerate(events)
        if i == len(events) - 1 or events[i + 1] - time > TWO_HOURS
    ]
    return events, valid


def extract_window(cgm, start, count):
    """Match a regular five-minute grid without compressing missing timestamps.

    Anchor at the first CGM timestamp at/after the requested start (within one
    sample). Reject windows with >20% missing, missing endpoints, or runs of
    >2 missing points. Remaining short interior gaps are interpolated later.
    """
    pos = cgm.index.searchsorted(start)
    if pos == len(cgm) or cgm.index[pos] - start >= FIVE_MINUTES:
        return None
    grid = pd.date_range(cgm.index[pos], periods=count, freq="5min")
    x = cgm.reindex(
        grid, method="nearest", tolerance=pd.Timedelta(seconds=90)
    ).to_numpy(dtype=float)
    missing = ~np.isfinite(x) | (x <= 0)
    if missing[0] or missing[-1] or missing.sum() > count * 0.2:
        return None
    run = 0
    for absent in missing:
        run = run + 1 if absent else 0
        if run > 2:
            return None
    x[missing] = np.nan
    return x


def extract_patient(cgm, insulin, patient):
    cgm = cgm.groupby(level=0).mean().sort_index()
    events, accepted = meal_starts(insulin)
    samples, labels, groups, starts = [], [], [], []
    stats = {
        "carb_events": len(events),
        "eligible_meals": len(accepted),
        "meal_kept": 0,
        "meal_rejected": 0,
        "no_meal_kept": 0,
        "no_meal_rejected": 0,
    }

    def add(start, count, label):
        x = extract_window(cgm, start, count)
        kind = "meal" if label else "no_meal"
        stats[kind + ("_kept" if x is not None else "_rejected")] += 1
        if x is not None:
            samples.append(x)
            labels.append(label)
            # Keep nearby observations in the same validation fold.
            groups.append(f"{patient}:{start.to_period('W')}")
            starts.append(start.isoformat())

    for t in accepted:
        add(t - HALF_HOUR, 30, 1)
    # Use ALL carb events, including excluded close meals, to bound negatives.
    # Reserve the next meal's 30-minute baseline to avoid shared CGM samples.
    if len(events) and len(cgm) and len(insulin):
        coverage_end = min(cgm.index[-1] + FIVE_MINUTES, insulin.index.max())
        for i, t in enumerate(events):
            end = coverage_end
            if i + 1 < len(events):
                end = min(events[i + 1] - HALF_HOUR, coverage_end)
            start = t + TWO_HOURS
            while start + TWO_HOURS <= end:
                add(start, 24, 0)
                start += TWO_HOURS
    return samples, labels, groups, starts, stats


def metrics(y, predictions):
    return {
        "accuracy": float(accuracy_score(y, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predictions)),
        "precision": float(precision_score(y, predictions, zero_division=0)),
        "recall": float(recall_score(y, predictions, zero_division=0)),
        "f1": float(f1_score(y, predictions, zero_division=0)),
        "confusion_matrix_labels_0_1": confusion_matrix(y, predictions, labels=[0, 1]).tolist(),
    }


def fit_machine(pipeline, samples, labels, indices):
    """Split before cropping; balance classes and preserve each original's weight."""
    rows, targets, weights = [], [], []
    counts = np.bincount(labels[indices], minlength=2)
    for i in indices:
        x = samples[i]
        variants = [x] if len(x) == 24 else [x, x[:24], x[3:27], x[6:30]]
        weight = len(indices) / (2 * counts[labels[i]] * len(variants))
        rows.extend(variants)
        targets.extend([labels[i]] * len(variants))
        weights.extend([weight] * len(variants))
    return clone(pipeline).fit(
        extract_features(rows), targets,
        standardscaler__sample_weight=weights,
        svc__sample_weight=weights,
    )


def purge_overlaps(training, validation, starts, samples, patients):
    """Remove training windows touching validation windows across week boundaries."""
    begin = pd.DatetimeIndex(starts).asi8 - pd.Timedelta(minutes=2).value
    # Include margins for alignment of the requested time to CGM samples.
    ends = begin + np.array([len(x) * 5 + 7 for x in samples]) * 60 * 1_000_000_000
    keep = []
    for i in training:
        other = validation[patients[validation] == patients[i]]
        if not np.any((begin[i] < ends[other]) & (ends[i] > begin[other])):
            keep.append(i)
    return np.asarray(keep, dtype=int)


def evaluate(pipeline, samples, y, groups, starts, patients):
    """Evaluate original and cropped windows without sharing training data."""
    features = extract_features(samples)
    predictions = np.empty(len(y), dtype=int)
    # Also measure 24-column meal windows to expose the train/test length shift.
    short_features = extract_features([x[:24] for x in samples])
    short_predictions = np.empty(len(y), dtype=int)
    last_features = extract_features([x[-24:] for x in samples])
    last_predictions = np.empty(len(y), dtype=int)
    folds = []
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=572)
    for fold, (training, validation) in enumerate(cv.split(features, y, groups), 1):
        training = purge_overlaps(training, validation, starts, samples, patients)
        machine = fit_machine(pipeline, samples, y, training)
        predictions[validation] = machine.predict(features[validation])
        short_predictions[validation] = machine.predict(short_features[validation])
        last_predictions[validation] = machine.predict(last_features[validation])
        scores = metrics(y[validation], predictions[validation])
        folds.append({
            "fold": fold,
            "train_rows": len(training),
            "validation_rows": len(validation),
            **scores,
        })
        print(
            f"Fold {fold}: accuracy={scores['accuracy']:.3f}, F1={scores['f1']:.3f}",
            flush=True,
        )
    cross_validation = {
        "method": (
            "5-fold StratifiedGroupKFold grouped by patient/week; overlapping "
            "windows purged; scaling and crop augmentation inside each fold"
        ),
        "folds": folds,
        "out_of_fold": metrics(y, predictions),
        "first_24_points_out_of_fold": metrics(y, short_predictions),
        "last_24_points_out_of_fold": metrics(y, last_predictions),
    }
    patient_holdout = {}
    for patient in (1, 2):
        held = patients == patient
        machine = fit_machine(pipeline, samples, y, np.flatnonzero(~held))
        patient_holdout[str(patient)] = metrics(
            y[held], machine.predict(short_features[held])
        )
    return cross_validation, patient_holdout


def train(
    data_dir=Path("."),
    model_path=Path(MODEL_PATH),
    report_path=Path("training_report.json"),
):
    samples, labels, groups, patients, starts = [], [], [], [], []
    report = {
        "extraction": {},
        "feature_names": FEATURE_NAMES,
        "versions": {
            "python": platform.python_version(),
            "scipy": scipy.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
    }
    for patient, (cgm_file, insulin_file) in enumerate(PATIENT_FILES, 1):
        batch, y, g, times, stats = extract_patient(
            read_export(data_dir / cgm_file, GLUCOSE),
            read_export(data_dir / insulin_file, CARBS),
            patient,
        )
        samples.extend(batch)
        labels.extend(y)
        groups.extend(g)
        starts.extend(times)
        patients.extend([patient] * len(y))
        report["extraction"][str(patient)] = stats
    y = np.asarray(labels)
    patients = np.asarray(patients)
    if len(np.unique(y)) != 2 or min(np.bincount(y)) < 5 or len(set(groups)) < 5:
        raise ValueError("Insufficient usable data for five-fold classification.")
    pipeline = make_pipeline(StandardScaler(), SVC(C=1.0, kernel="rbf"))
    report["cross_validation"], report["patient_holdout"] = evaluate(
        pipeline, samples, y, groups, starts, patients
    )
    pipeline = fit_machine(pipeline, samples, y, np.arange(len(y)))
    artifact = {
        "pipeline": pipeline,
        "feature_version": FEATURE_VERSION,
        "feature_names": FEATURE_NAMES,
        "fallback_label": int(np.bincount(y).argmax()),
        "versions": report["versions"],
    }
    with open(model_path, "wb") as stream:
        pickle.dump(artifact, stream, protocol=pickle.HIGHEST_PROTOCOL)
    report["training_rows"] = len(y)
    report["class_counts"] = {
        "no_meal": int((y == 0).sum()),
        "meal": int((y == 1).sum()),
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Saved {model_path} and {report_path}; trained on {len(y)} windows.")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("."))
    parser.add_argument("--model", type=Path, default=Path(MODEL_PATH))
    parser.add_argument("--report", type=Path, default=Path("training_report.json"))
    args = parser.parse_args()
    train(args.data_dir, args.model, args.report)


if __name__ == "__main__":
    main()
