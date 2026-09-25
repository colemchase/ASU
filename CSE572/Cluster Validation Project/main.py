#!/usr/bin/env python3
"""Cluster-validation baseline for the CSE 572 meal dataset.

The script reads the supplied ZIP without extracting it into the repository,
constructs 30-point CGM meal windows, transforms them with the Project 2
feature schema, then fits KMeans and DBSCAN.
"""

from __future__ import annotations

import argparse
import io
import zipfile
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


DATA_ARCHIVE = "CSE 572_Cluster Validation Project Files.zip"
CGM_FILE = "CGMData.csv"
INSULIN_FILE = "InsulinData.csv"
CGM_MEMBER = "Project 3 Files/CGMData.csv"
INSULIN_MEMBER = "Project 3 Files/InsulinData.csv"
WINDOW_START_MINUTES = -30
WINDOW_POINTS = 30
CADENCE_MINUTES = 5

# This is the Project 2 feature schema, retained here so this submission is
# self-contained.  Project 3 receives complete 30-reading meal windows, while
# Project 2's helper also supports its 24-reading no-meal/test windows.
FEATURE_NAMES = [
    "mean", "std", "range", "coefficient_of_variation", "iqr",
    "relative_peak_rise", "relative_end_change", "peak_position",
    "trough_position", "linear_slope", "max_rise_rate", "max_fall_rate",
    "mean_absolute_rate", "rate_std", "curvature_std", "positive_rate_fraction",
    "first_to_middle", "middle_to_last", "baseline_relative_area",
    "fft_1", "fft_2", "fft_3", "fft_4", "spectral_entropy",
]


def read_project_data(archive_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read Ed workspace CSVs, with the supplied local ZIP as a fallback."""
    cgm_path = Path(CGM_FILE)
    insulin_path = Path(INSULIN_FILE)
    if cgm_path.is_file() and insulin_path.is_file():
        return (
            pd.read_csv(cgm_path, low_memory=False),
            pd.read_csv(insulin_path, low_memory=False),
        )
    if not archive_path.is_file():
        raise FileNotFoundError(
            f"Expected {CGM_FILE} and {INSULIN_FILE}, or archive {archive_path}."
        )
    with zipfile.ZipFile(archive_path) as archive:
        cgm = pd.read_csv(io.BytesIO(archive.read(CGM_MEMBER)), low_memory=False)
        insulin = pd.read_csv(
            io.BytesIO(archive.read(INSULIN_MEMBER)), low_memory=False
        )
    return cgm, insulin


def add_timestamp(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["timestamp"] = pd.to_datetime(
        result["Date"].astype(str) + " " + result["Time"].astype(str),
        format="%m/%d/%Y %H:%M:%S",
        errors="coerce",
    )
    return result.dropna(subset=["timestamp"]).sort_values("timestamp")


def meal_events(insulin: pd.DataFrame) -> pd.DataFrame:
    """Select carb entries that have no later meal within the next two hours."""
    insulin = add_timestamp(insulin)
    meals = insulin.loc[
        pd.to_numeric(insulin["BWZ Carb Input (grams)"], errors="coerce").gt(0),
        ["timestamp", "BWZ Carb Input (grams)"],
    ].copy()
    meals["carbs"] = pd.to_numeric(meals["BWZ Carb Input (grams)"], errors="coerce")
    meals = meals.dropna(subset=["carbs"]).drop_duplicates("timestamp").sort_values("timestamp")

    # A meal with another carb entry during its two-hour response window cannot
    # be attributed to a single amount of carbohydrates.
    next_meal = meals["timestamp"].shift(-1)
    return meals.loc[
        next_meal.isna() | ((next_meal - meals["timestamp"]) >= pd.Timedelta(hours=2)),
        ["timestamp", "carbs"],
    ].reset_index(drop=True)


def build_meal_windows(cgm: pd.DataFrame, meals: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Build 30 CGM readings from 30 minutes before each qualifying meal."""
    cgm = add_timestamp(cgm)
    readings = cgm.loc[:, ["timestamp", "Sensor Glucose (mg/dL)"]].copy()
    readings["glucose"] = pd.to_numeric(readings["Sensor Glucose (mg/dL)"], errors="coerce")
    readings = readings.dropna(subset=["glucose"]).sort_values("timestamp")

    windows: list[np.ndarray] = []
    carbs: list[float] = []
    offsets = pd.to_timedelta(
        np.arange(WINDOW_START_MINUTES, WINDOW_START_MINUTES + WINDOW_POINTS * CADENCE_MINUTES, CADENCE_MINUTES),
        unit="min",
    )

    for meal in meals.itertuples(index=False):
        targets = pd.DataFrame({"target": meal.timestamp + offsets})
        aligned = pd.merge_asof(
            targets.sort_values("target"),
            readings,
            left_on="target",
            right_on="timestamp",
            direction="nearest",
            tolerance=pd.Timedelta(minutes=2, seconds=30),
        )
        if aligned["glucose"].notna().all():
            windows.append(aligned["glucose"].to_numpy(dtype=float))
            carbs.append(float(meal.carbs))

    if not windows:
        raise ValueError("No complete 30-point meal windows were found.")
    return np.vstack(windows), np.asarray(carbs)


def project2_features(meal_windows: np.ndarray) -> np.ndarray:
    """Apply Project 2's 24-feature transformation to complete meal windows.

    A complete finite 30-point window is already required by
    :func:`build_meal_windows`, so no imputation is needed here.
    """
    rows: list[list[float]] = []
    for sample in meal_windows:
        x = np.asarray(sample, dtype=float)
        if x.shape != (WINDOW_POINTS,) or not np.isfinite(x).all() or (x <= 0).any():
            raise ValueError("Project 2 features require complete positive 30-point meal windows.")
        n = len(x)
        mean = float(x.mean())
        baseline = float(x[:3].mean())
        differences = np.diff(x) / CADENCE_MINUTES
        spectrum = np.abs(np.fft.rfft(x - mean))[1:] / n
        power = spectrum**2
        total_power = float(power.sum())
        if total_power > 0:
            probabilities = power[power > 0] / total_power
            spectral_entropy = float(
                -np.sum(probabilities * np.log(probabilities)) / np.log(len(power))
            )
        else:
            spectral_entropy = 0.0
        thirds = [float(part.mean()) for part in np.array_split(x, 3)]
        times = np.arange(n) * CADENCE_MINUTES
        slope = float(
            np.dot(times - times.mean(), x - mean) / np.sum((times - times.mean()) ** 2)
        )
        rows.append([
            mean, float(x.std()), float(np.ptp(x)), float(x.std() / mean),
            float(np.percentile(x, 75) - np.percentile(x, 25)),
            float((x.max() - baseline) / baseline),
            float((x[-3:].mean() - baseline) / baseline),
            float(x.argmax() / (n - 1)), float(x.argmin() / (n - 1)), slope,
            float(differences.max()), float(differences.min()), float(np.abs(differences).mean()),
            float(differences.std()), float(np.diff(differences).std()),
            float(np.mean(differences > 0)), thirds[1] - thirds[0],
            thirds[2] - thirds[1], float(np.mean(x - baseline) / baseline),
            *spectrum[:4].tolist(), spectral_entropy,
        ])
    return np.asarray(rows, dtype=float).reshape(-1, len(FEATURE_NAMES))


def carbohydrate_range(insulin: pd.DataFrame) -> tuple[float, float]:
    """Get the required global meal-carb range before filtering CGM windows."""
    carbs = pd.to_numeric(insulin["BWZ Carb Input (grams)"], errors="coerce")
    carbs = carbs[carbs.gt(0)]
    if carbs.empty:
        raise ValueError("No positive carbohydrate entries were found.")
    return float(carbs.min()), float(carbs.max())


def carbohydrate_bins(
    carbs: np.ndarray, minimum: float, maximum: float
) -> tuple[np.ndarray, int]:
    """Create 20-gram labels anchored at the global meal-carb minimum."""
    bin_count = max(1, int(np.ceil((maximum - minimum) / 20.0)))
    labels = np.minimum(((carbs - minimum) // 20).astype(int), bin_count - 1)
    return labels, bin_count


def total_sse(features: np.ndarray, labels: np.ndarray, *, include_noise: bool = False) -> float:
    """Sum within-cluster squared distances to each cluster mean.

    DBSCAN noise (label -1) is excluded by default because it is deliberately
    not assigned to a density cluster.
    """
    total = 0.0
    for label in np.unique(labels):
        if label == -1 and not include_noise:
            continue
        points = features[labels == label]
        if len(points):
            center = points.mean(axis=0)
            total += float(np.square(points - center).sum())
    return total


def entropy_and_purity(true_bins: np.ndarray, cluster_labels: np.ndarray) -> tuple[float, float]:
    """Return size-weighted entropy and global purity for a clustering."""
    total = len(true_bins)
    entropy = 0.0
    correct = 0
    for cluster in np.unique(cluster_labels):
        members = true_bins[cluster_labels == cluster]
        counts = np.bincount(members)
        probabilities = counts[counts > 0] / len(members)
        entropy += (len(members) / total) * float(-(probabilities * np.log2(probabilities)).sum())
        correct += int(counts.max())
    return entropy, correct / total


def select_dbscan(
    features: np.ndarray,
    eps_values: list[float],
    min_samples_values: list[int],
    target_cluster_count: int,
) -> tuple[DBSCAN, pd.DataFrame]:
    """Choose an n-cluster DBSCAN fit with minimal noise, then best silhouette."""
    trials: list[dict[str, float | int]] = []
    best: tuple[float, float, DBSCAN] | None = None

    for eps, min_samples in product(eps_values, min_samples_values):
        model = DBSCAN(eps=eps, min_samples=min_samples).fit(features)
        labels = model.labels_
        non_noise = labels != -1
        cluster_count = len(set(labels[non_noise]))
        score = np.nan
        if (
            cluster_count == target_cluster_count
            and non_noise.sum() > cluster_count
        ):
            score = float(silhouette_score(features[non_noise], labels[non_noise]))
            noise_fraction = float((labels == -1).mean())
            candidate = (noise_fraction, -score, model)
            if best is None or candidate[:2] < best[:2]:
                best = candidate
        trials.append(
            {
                "eps": eps,
                "min_samples": min_samples,
                "clusters": cluster_count,
                "noise_fraction": float((labels == -1).mean()),
                "silhouette": score,
                "matches_required_cluster_count": cluster_count == target_cluster_count,
            }
        )

    if best is None:
        raise ValueError(
            f"No DBSCAN parameter pair produced the required {target_cluster_count} clusters."
        )
    return best[2], pd.DataFrame(trials).sort_values(
        ["matches_required_cluster_count", "noise_fraction", "silhouette"],
        ascending=[False, True, False],
        na_position="last",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, default=Path(DATA_ARCHIVE))
    parser.add_argument("--result", type=Path, default=Path("Result.csv"))
    parser.add_argument("--grid", type=Path, default=Path("dbscan_grid.csv"))
    args = parser.parse_args()

    cgm, insulin = read_project_data(args.archive)
    minimum_carbs, maximum_carbs = carbohydrate_range(insulin)
    windows, carbs = build_meal_windows(cgm, meal_events(insulin))
    true_bins, cluster_count = carbohydrate_bins(carbs, minimum_carbs, maximum_carbs)

    features = StandardScaler().fit_transform(project2_features(windows))

    kmeans = KMeans(n_clusters=cluster_count, random_state=0, n_init=20).fit(features)
    dbscan, grid = select_dbscan(
        features,
        eps_values=[round(value, 1) for value in np.arange(0.8, 4.1, 0.1)],
        min_samples_values=list(range(3, 11)),
        target_cluster_count=cluster_count,
    )

    k_entropy, k_purity = entropy_and_purity(true_bins, kmeans.labels_)
    d_entropy, d_purity = entropy_and_purity(true_bins, dbscan.labels_)
    result = [
        total_sse(features, kmeans.labels_),
        total_sse(features, dbscan.labels_),
        k_entropy,
        d_entropy,
        k_purity,
        d_purity,
    ]
    pd.DataFrame([result]).to_csv(args.result, header=False, index=False)
    grid.to_csv(args.grid, index=False)

    print(f"Meal windows retained: {len(windows)}")
    print(f"Carbohydrate bins / KMeans clusters: {cluster_count}")
    print(f"DBSCAN: eps={dbscan.eps}, min_samples={dbscan.min_samples}")
    print(f"Wrote {args.result} and {args.grid}")


if __name__ == "__main__":
    main()
