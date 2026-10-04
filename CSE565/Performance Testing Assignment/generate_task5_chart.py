#!/usr/bin/env python3
"""Create a Task 5 time-series chart from Locust's aggregate history CSV."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt

def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: generate_task5_chart.py <locust_stats_history.csv> <output.png>")
    source, destination = Path(sys.argv[1]), Path(sys.argv[2])
    rows: list[dict[str, str]] = []
    with source.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["Name"] == "Aggregated" and row["Type"] == "":
                rows.append(row)
    if len(rows) < 2:
        raise SystemExit("Expected at least two aggregate Locust history rows.")

    started = int(rows[0]["Timestamp"])
    seconds = [int(row["Timestamp"]) - started for row in rows]
    rps = [float(row["Requests/s"]) for row in rows]
    failures = [float(row["Failures/s"]) for row in rows]
    average_ms = [float(row["Total Average Response Time"]) for row in rows]
    panels = [
        ("Aggregate requests per second", rps, "#1769aa", "RPS"),
        ("SLO failures per second", failures, "#c73e1d", "Failures/s"),
        ("Aggregate average response time", average_ms, "#6a3d9a", "Milliseconds"),
    ]
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True, layout="constrained")
    for axis, (title, values, color, label) in zip(axes, panels):
        axis.plot(seconds, values, color=color, linewidth=1.75)
        axis.set_title(title, loc="left", fontsize=12, fontweight="bold")
        axis.set_ylabel(label)
        axis.grid(axis="y", alpha=0.3)
    axes[-1].set_xlabel("Elapsed seconds")
    figure.suptitle("Task 5: 10,000-User Sustained Load with a 500 ms SLO", fontsize=15, fontweight="bold")
    figure.savefig(destination, dpi=200, bbox_inches="tight")


if __name__ == "__main__":
    main()
