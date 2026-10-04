"""Create a clear Task 5 SLO-results figure from the Locust statistics CSV."""

from __future__ import annotations

import csv
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/cse565-matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


INPUT = Path("locust_results/task5-slo-10000-60s/locust_stats.csv")
OUTPUT = Path("screenshots/task5_slo_results.png")


def main() -> None:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["Name"] and row["Name"] != "Aggregated"]

    names = [row["Name"] for row in rows]
    average_ms = [float(row["Average Response Time"]) for row in rows]
    failure_rate = [float(row["Failure Count"]) / float(row["Request Count"]) * 100 for row in rows]
    colors = ["#e76f51" if rate else "#457b9d" for rate in failure_rate]

    figure, (latency_ax, failure_ax) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    figure.suptitle("Task 5: 10,000 Immediate Users for 60 Seconds with a 500 ms SLO", fontsize=14, fontweight="bold")

    latency_ax.bar(names, average_ms, color=colors)
    latency_ax.axhline(500, color="#d62828", linestyle="--", linewidth=1.5, label="500 ms SLO")
    latency_ax.set_ylabel("Average response time (ms)")
    latency_ax.grid(axis="y", alpha=0.25)
    latency_ax.legend(loc="upper right")

    bars = failure_ax.bar(names, failure_rate, color=colors)
    failure_ax.set_ylabel("SLO failures (%)")
    failure_ax.set_ylim(0, 70)
    failure_ax.grid(axis="y", alpha=0.25)
    failure_ax.tick_params(axis="x", rotation=20)
    for bar, rate in zip(bars, failure_rate):
        if rate:
            failure_ax.text(bar.get_x() + bar.get_width() / 2, rate + 1, f"{rate:.1f}%", ha="center", va="bottom")

    figure.text(0.5, 0.01, "Only the database-query and API-request tasks exceeded the 500 ms response-time SLO.", ha="center", fontsize=9)
    figure.tight_layout(rect=(0, 0.05, 1, 0.93))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=180)


if __name__ == "__main__":
    main()
