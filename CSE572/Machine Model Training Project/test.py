"""Predict meal (1) or no meal (0) for every row of test.csv."""
import argparse
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

MODEL_PATH = "model.pkl"
FEATURE_VERSION = 1
FEATURE_NAMES = [
    "mean", "std", "range", "coefficient_of_variation", "iqr",
    "relative_peak_rise", "relative_end_change", "peak_position",
    "trough_position", "linear_slope", "max_rise_rate", "max_fall_rate",
    "mean_absolute_rate", "rate_std", "curvature_std", "positive_rate_fraction",
    "first_to_middle", "middle_to_last", "baseline_relative_area",
    "fft_1", "fft_2", "fft_3", "fft_4", "spectral_entropy",
]


def fill_sample(sample):
    """Interpolate within a row; extend nearest values at missing endpoints."""
    x = np.asarray(sample, dtype=float).copy()
    if x.ndim != 1 or len(x) not in (24, 30):
        raise ValueError("Each sample must contain 24 or 30 glucose values.")
    x[~np.isfinite(x) | (x <= 0)] = np.nan
    good = np.flatnonzero(np.isfinite(x))
    if not len(good):
        raise ValueError("A sample must have at least one valid glucose value.")
    return np.interp(np.arange(len(x)), good, x[good])


def extract_features(samples):
    """Same 24 features for 24- and 30-point, chronological CGM windows.

    Statistics use the entire window. Positions and spectral amplitudes are
    normalized by length; glucose derivatives retain the five-minute cadence.
    No labels or statistics from other rows enter feature extraction.
    """
    rows = []
    for sample in samples:
        x = fill_sample(sample)
        n = len(x)
        mean = x.mean()
        baseline = x[:3].mean()
        d = np.diff(x) / 5.0
        spectrum = np.abs(np.fft.rfft(x - mean))[1:] / n
        power = spectrum**2
        total = power.sum()
        if total > 0:
            probabilities = power[power > 0] / total
            entropy = -np.sum(probabilities * np.log(probabilities)) / np.log(len(power))
        else:
            entropy = 0.0
        thirds = [part.mean() for part in np.array_split(x, 3)]
        t = np.arange(n) * 5.0
        slope = np.dot(t - t.mean(), x - mean) / np.sum((t - t.mean()) ** 2)
        rows.append([
            mean, x.std(), np.ptp(x), x.std() / mean,
            np.percentile(x, 75) - np.percentile(x, 25),
            (x.max() - baseline) / baseline, (x[-3:].mean() - baseline) / baseline,
            x.argmax() / (n - 1), x.argmin() / (n - 1), slope,
            d.max(), d.min(), np.abs(d).mean(), d.std(),
            np.diff(d).std(), np.mean(d > 0),
            thirds[1] - thirds[0], thirds[2] - thirds[1],
            np.mean(x - baseline) / baseline,
            *spectrum[:4], entropy,
        ])
    return np.asarray(rows, dtype=float).reshape(-1, len(FEATURE_NAMES))


def load_model(path=MODEL_PATH):
    """Load the model produced by train.py and check its feature schema."""
    with open(path, "rb") as stream:
        artifact = pickle.load(stream)
    if (
        artifact["feature_version"] != FEATURE_VERSION
        or artifact["feature_names"] != FEATURE_NAMES
    ):
        raise ValueError("Model feature schema does not match test.py; retrain the model.")
    return artifact


def predict_sample(sample, model=None):
    """Return one integer label; callers may reuse an already loaded artifact."""
    artifact = load_model() if model is None else model
    x = np.asarray(sample, dtype=float)
    if x.shape != (24,):
        raise ValueError("Test samples must contain exactly 24 glucose values.")
    return int(predict_samples(x.reshape(1, 24), artifact)[0])


def predict_samples(samples, artifact):
    """Predict a batch, using the majority label for entirely missing rows."""
    usable = np.any(np.isfinite(samples) & (samples > 0), axis=1)
    predictions = np.full(len(samples), artifact["fallback_label"], dtype=int)
    if usable.any():
        features = extract_features(samples[usable])
        predictions[usable] = artifact["pipeline"].predict(features)
    return predictions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="test.csv")
    parser.add_argument("--output", default="Result.csv")
    parser.add_argument("--model", default=MODEL_PATH)
    args = parser.parse_args()
    artifact = load_model(args.model)
    try:
        data = pd.read_csv(args.input, header=None)
    except pd.errors.EmptyDataError:
        Path(args.output).write_text("")
        return
    if data.shape[1] != 24:
        raise ValueError(f"Expected 24 columns in {args.input}; found {data.shape[1]}.")
    samples = data.apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    predictions = predict_samples(samples, artifact)
    np.savetxt(args.output, predictions, fmt="%d")
    print(f"Wrote {len(predictions)} predictions to {args.output}")


if __name__ == "__main__":
    main()
