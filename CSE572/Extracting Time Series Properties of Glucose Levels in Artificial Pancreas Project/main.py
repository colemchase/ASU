import pandas as pd
import numpy as np


CGM_FILE = "CSE572/Extracting Time Series Properties of Glucose Levels in Artificial Pancreas Project/data/CGMData.csv"
INSULIN_FILE = "CSE572/Extracting Time Series Properties of Glucose Levels in Artificial Pancreas Project/data/InsulinData.csv"
OUTPUT_FILE = "CSE572/Extracting Time Series Properties of Glucose Levels in Artificial Pancreas Project/data/Result.csv"


def load_data():
    cgm_df = pd.read_csv(CGM_FILE, usecols=["Date", "Time", "Sensor Glucose (mg/dL)"])
    insulin_df = pd.read_csv(INSULIN_FILE, usecols=["Date", "Time", "Alarm"])
    cgm_df["Timestamp"] = pd.to_datetime(
        cgm_df["Date"] + " " + cgm_df["Time"],
        format="%m/%d/%Y %H:%M:%S",
    )
    insulin_df["Timestamp"] = pd.to_datetime(
        insulin_df["Date"] + " " + insulin_df["Time"],
        format="%m/%d/%Y %H:%M:%S",
    )
    return cgm_df, insulin_df


def find_auto_mode_start(insulin_df):
    auto_mode_rows = insulin_df["Alarm"].eq("AUTO MODE ACTIVE PLGM OFF")
    return insulin_df.loc[auto_mode_rows, "Timestamp"].min()


def find_matching_cgm_start(cgm_df, auto_start_time):
    matching_timestamps = cgm_df.loc[cgm_df["Timestamp"].ge(auto_start_time), "Timestamp"]
    return matching_timestamps.min()


def split_modes(cgm_df, cgm_auto_start_time):
    auto_mode_mask = cgm_df["Timestamp"].ge(cgm_auto_start_time)
    return cgm_df.loc[~auto_mode_mask], cgm_df.loc[auto_mode_mask]


def compute_metrics_for_mode(mode_df):
    if mode_df.empty:
        return [0.0] * 18

    daily_metrics = []
    for _, day_df in mode_df.groupby(mode_df["Timestamp"].dt.date, sort=False):
        hours = day_df["Timestamp"].dt.hour.to_numpy()
        daily_metrics.append(
            compute_window_metrics(day_df.loc[hours < 6])
            + compute_window_metrics(day_df.loc[hours >= 6])
            + compute_window_metrics(day_df)
        )

    return np.mean(daily_metrics, axis=0).tolist()


def compute_window_metrics(day_df):
    values = day_df["Sensor Glucose (mg/dL)"].to_numpy(dtype=float)
    scale = 100.0 / 288
    return [
        float(np.count_nonzero(values > 180) * scale),
        float(np.count_nonzero(values > 250) * scale),
        float(np.count_nonzero((values >= 70) & (values <= 180)) * scale),
        float(np.count_nonzero((values >= 70) & (values <= 150)) * scale),
        float(np.count_nonzero(values < 70) * scale),
        float(np.count_nonzero(values < 54) * scale),
    ]


def write_results(manual_metrics, auto_metrics):
    pd.DataFrame([manual_metrics, auto_metrics]).to_csv(
        OUTPUT_FILE,
        header=False,
        index=False,
    )


def main():
    cgm_df, insulin_df = load_data()

    auto_start_time = find_auto_mode_start(insulin_df)
    cgm_auto_start_time = find_matching_cgm_start(cgm_df, auto_start_time)

    manual_df, auto_df = split_modes(cgm_df, cgm_auto_start_time)

    manual_metrics = compute_metrics_for_mode(manual_df)
    auto_metrics = compute_metrics_for_mode(auto_df)

    write_results(manual_metrics, auto_metrics)


if __name__ == "__main__":
    main()
