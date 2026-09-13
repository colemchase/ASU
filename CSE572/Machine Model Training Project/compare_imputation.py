"""Compare training-meal imputation on identical, complete-meal validation rows.

No-meal handling, features, crop augmentation and SVM settings stay fixed.
Incomplete meal validation rows are excluded for every method. KNN donors are
only training meals. No validation labels are needed to impute test inputs:
this experiment changes training-data preparation, not test-time imputation.
"""
import json
from pathlib import Path

import numpy as np
from sklearn.impute import KNNImputer
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from train import (
    CARBS, GLUCOSE, PATIENT_FILES, extract_patient, fit_machine,
    metrics, purge_overlaps, read_export,
)
from test import extract_features, fill_sample

METHODS = ('drop', 'linear', 'polynomial', 'knn')


def polynomial_fill(sample):
    """Fit degree two to observed points; replace gaps only, without extrapolation."""
    x = np.asarray(sample, dtype=float).copy()
    good = np.isfinite(x) & (x > 0)
    if good.all():
        return x
    if good.sum() < 3 or not good[0] or not good[-1]:
        raise ValueError('Quadratic filling requires observed endpoints and >=3 values.')
    t = np.linspace(-1, 1, len(x))
    curve = np.polynomial.Polynomial.fit(t[good], x[good], deg=2)
    # Avoid creating values outside the observed window's glucose range.
    x[~good] = np.clip(curve(t[~good]), x[good].min(), x[good].max())
    return x


def prepare_training(samples, y, indices, method):
    prepared = list(samples)
    meals = indices[y[indices] == 1]
    incomplete = [i for i in meals if np.isnan(samples[i]).any()]
    if method == 'drop':
        excluded = set(incomplete)
        return prepared, np.array([i for i in indices if i not in excluded]), None
    imputer = None
    if method == 'knn':
        imputer = KNNImputer(n_neighbors=5, weights='distance')
        # Same 30-point alignment and glucose units; only training-fold donors.
        imputer.fit(np.stack([samples[i] for i in meals]))
        if incomplete:
            filled = imputer.transform(np.stack([samples[i] for i in incomplete]))
            for i, row in zip(incomplete, filled):
                prepared[i] = row
    else:
        fill = polynomial_fill if method == 'polynomial' else fill_sample
        for i in incomplete:
            prepared[i] = fill(samples[i])
    return prepared, indices, imputer


def main():
    samples, labels, groups, starts, patients = [], [], [], [], []
    for patient, (cgm_file, insulin_file) in enumerate(PATIENT_FILES, 1):
        batch, y, g, times, _ = extract_patient(
            read_export(cgm_file, GLUCOSE), read_export(insulin_file, CARBS),
            patient, require_complete_meals=False,
        )
        samples.extend(batch)
        labels.extend(y)
        groups.extend(g)
        starts.extend(times)
        patients.extend([patient] * len(y))
    y, patients = np.asarray(labels), np.asarray(patients)
    complete = np.array([np.isfinite(x).all() for x in samples])
    eligible = (y == 0) | complete
    features = {
        'first_24': extract_features([x[:24] for x in samples]),
        'last_24': extract_features([x[-24:] for x in samples]),
    }
    pipeline = make_pipeline(StandardScaler(), SVC(C=1.0, kernel='rbf'))
    results = {m: {'folds': [], 'patient_holdout': {}} for m in METHODS}
    predictions = {m: {view: np.full(len(y), -1, dtype=int) for view in features} for m in METHODS}
    reconstruction = {m: [] for m in METHODS if m != 'drop'}
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=572)
    splits = list(cv.split(np.zeros(len(y)), y, groups))
    for fold, (training, validation_all) in enumerate(splits, 1):
        training = purge_overlaps(training, validation_all, starts, samples, patients)
        validation = validation_all[eligible[validation_all]]
        # Artificial short gaps give a known target for an independent filling check.
        held_meals = validation[y[validation] == 1]
        originals = np.stack([samples[i] for i in held_meals])
        masked = originals.copy()
        mask = np.zeros(masked.shape, dtype=bool)
        rng = np.random.default_rng(572 + fold)
        for row in range(len(masked)):
            start = rng.integers(2, 27)
            mask[row, start:start + int(rng.integers(1, 3))] = True
        masked[mask] = np.nan
        for method in METHODS:
            prepared, selected, imputer = prepare_training(samples, y, training, method)
            model = fit_machine(pipeline, prepared, y, selected)
            for view, matrix in features.items():
                predictions[method][view][validation] = model.predict(matrix[validation])
            scores = metrics(y[validation], predictions[method]['first_24'][validation])
            results[method]['folds'].append({
                'fold': fold, 'training_rows': len(selected),
                'validation_rows': len(validation), **scores,
            })
            if method != 'drop':
                if method == 'knn':
                    filled = imputer.transform(masked)
                else:
                    fill = polynomial_fill if method == 'polynomial' else fill_sample
                    filled = np.stack([fill(row) for row in masked])
                reconstruction[method].extend((filled[mask] - originals[mask]).tolist())
            print(f"Fold {fold} {method}: accuracy={scores['accuracy']:.3f}, F1={scores['f1']:.3f}", flush=True)
    for method in METHODS:
        results[method]['out_of_fold'] = {
            view: metrics(y[eligible], values[eligible])
            for view, values in predictions[method].items()
        }
        for patient in (1, 2):
            training = np.flatnonzero(patients != patient)
            validation = np.flatnonzero((patients == patient) & eligible)
            prepared, selected, _ = prepare_training(samples, y, training, method)
            model = fit_machine(pipeline, prepared, y, selected)
            results[method]['patient_holdout'][str(patient)] = metrics(
                y[validation], model.predict(features['first_24'][validation]))
        if method != 'drop':
            errors = np.asarray(reconstruction[method])
            results[method]['synthetic_gap_reconstruction'] = {
                'masked_points': len(errors), 'mae_mg_dl': float(np.abs(errors).mean()),
                'rmse_mg_dl': float(np.sqrt(np.mean(errors**2))),
            }
    report = {
        'protocol': __doc__,
        'settings': {'polynomial_degree': 2, 'polynomial_clip': 'observed window min/max',
                     'knn_neighbors': 5, 'knn_weights': 'distance'},
        'original_windows': len(y), 'common_validation_windows': int(eligible.sum()),
        'incomplete_meal_windows': int(((y == 1) & ~complete).sum()),
        'notes': 'Fixed configurations. Scores use identical folds and validation rows; do not compare directly with older reports that used different folds. Synthetic gaps are a reconstruction diagnostic, not hidden-test performance. Production model is unchanged.',
        'methods': results,
    }
    Path('imputation_comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    for method in METHODS:
        print(method, results[method]['out_of_fold']['first_24'], flush=True)


if __name__ == '__main__':
    main()
