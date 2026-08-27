import pandas as pd
import numpy as np


CGM_FILE = "your_folder_name/CGMData.csv"
INSULIN_FILE = "your_folder_name/InsulinData.csv"
OUTPUT_FILE = "Result.csv"


def load_data():
    # TODO: read both CSV files into pandas DataFrames
    # TODO: combine Date + Time into one timestamp column for each DataFrame
    pass


def find_auto_mode_start(insulin_df):
    # TODO: filter insulin rows where Alarm contains/equals:
    # "AUTO MODE ACTIVE PLGM OFF"
    # TODO: find the earliest timestamp among those rows
    pass


def find_matching_cgm_start(cgm_df, auto_start_time):
    # TODO: find the nearest CGM timestamp that is >= auto_start_time
    pass


def split_modes(cgm_df, cgm_auto_start_time):
    # TODO: manual mode = timestamps before auto start
    # TODO: auto mode = timestamps from auto start onward
    pass


def compute_metrics_for_mode(mode_df):
    # TODO: compute 18 values:
    # overnight 6 metrics
    # daytime 6 metrics
    # whole day 6 metrics
    pass


def compute_window_metrics(day_df):
    # TODO: given one time-window DataFrame, count glucose values in each range
    # TODO: divide counts by 288
    pass


def write_results(manual_metrics, auto_metrics):
    # TODO: write two rows, no header, no index
    pass


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