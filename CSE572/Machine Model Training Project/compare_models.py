"""Compare fixed SVM and tree configurations using the same validation protocol."""
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from train import CARBS, GLUCOSE, PATIENT_FILES, evaluate, extract_patient, read_export


def main():
    samples, labels, groups, starts, patients = [], [], [], [], []
    extraction = {}
    for patient, (cgm_file, insulin_file) in enumerate(PATIENT_FILES, 1):
        batch, targets, batch_groups, times, stats = extract_patient(
            read_export(cgm_file, GLUCOSE),
            read_export(insulin_file, CARBS),
            patient,
        )
        samples.extend(batch)
        labels.extend(targets)
        groups.extend(batch_groups)
        starts.extend(times)
        patients.extend([patient] * len(targets))
        extraction[str(patient)] = stats

    # Fix settings before evaluating. The constrained tree checks whether
    # controlling tree complexity helps compared with the default deep tree.
    configurations = {
        "svm_rbf": (SVC, {"C": 1.0, "kernel": "rbf", "gamma": "scale"}),
        "tree_default": (DecisionTreeClassifier, {"random_state": 572}),
        "tree_constrained": (
            DecisionTreeClassifier,
            {"max_depth": 5, "min_samples_leaf": 20, "random_state": 572},
        ),
    }
    report = {
        "notes": (
            "Fixed configurations, not a hyperparameter search. All models use "
            "identical original windows, purged patient/week folds, crop "
            "augmentation, scaling, and sample weights. Trees do not require "
            "scaling; it is retained to keep preprocessing consistent. These "
            "are development comparisons, not untouched test-set estimates."
        ),
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "extraction": extraction,
        "class_counts": {
            "no_meal": labels.count(0),
            "meal": labels.count(1),
        },
        "models": {},
    }
    for name, (classifier, parameters) in configurations.items():
        print(f"Evaluating {name}: {parameters}", flush=True)
        pipeline = make_pipeline(StandardScaler(), classifier(**parameters))
        validation, holdout = evaluate(
            pipeline, samples, np.asarray(labels), groups, starts,
            np.asarray(patients),
        )
        report["models"][name] = {
            "parameters": parameters,
            "cross_validation": validation,
            "patient_holdout": holdout,
        }
        scores = validation["first_24_points_out_of_fold"]
        print(
            f"24-point accuracy={scores['accuracy']:.4f}, "
            f"F1={scores['f1']:.4f}, recall={scores['recall']:.4f}",
            flush=True,
        )

    path = Path("model_comparison.json")
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
