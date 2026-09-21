#!/usr/bin/env python3
"""Validate rows and pairwise coverage for the CSE 565 DOE model."""

from __future__ import annotations

import csv
import itertools
import sys
from pathlib import Path


FACTORS = {
    "Type of Phone": {
        "iPhone 14", "iPhone 13", "Galaxy Z", "Huawei Mate", "Google Pixel 7"
    },
    "Authentication": {"Fingerprint", "Face recognition", "Text Password"},
    "Connectivity": {"Wireless", "3G", "4G LTE", "5G Edge"},
    "Memory": {"128 GB", "256 GB", "512 GB", "1 TB"},
    "Battery Level": {"<20%", "20-39%", "40-59%", "60-79%", "80-100%"},
}


def required_pairs() -> set[tuple[str, str, str, str]]:
    pairs: set[tuple[str, str, str, str]] = set()
    for left, right in itertools.combinations(FACTORS, 2):
        pairs.update(
            (left, left_value, right, right_value)
            for left_value in FACTORS[left]
            for right_value in FACTORS[right]
        )
    return pairs


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} TEST_CASES.tsv")
        return 2

    test_cases = Path(sys.argv[1])
    with test_cases.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))

    expected_headers = list(FACTORS)
    if not rows or list(rows[0]) != expected_headers:
        print(f"Invalid header. Expected: {expected_headers}")
        return 1

    invalid_values: list[str] = []
    covered: set[tuple[str, str, str, str]] = set()
    normalized_rows: list[tuple[str, ...]] = []
    for row_number, row in enumerate(rows, start=2):
        normalized_rows.append(tuple(row[factor] for factor in FACTORS))
        for factor, allowed_values in FACTORS.items():
            if row[factor] not in allowed_values:
                invalid_values.append(
                    f"row {row_number}, {factor}: {row[factor]!r} is not allowed"
                )
        for left, right in itertools.combinations(FACTORS, 2):
            covered.add((left, row[left], right, row[right]))

    required = required_pairs()
    missing = sorted(required - covered)
    duplicates = len(normalized_rows) - len(set(normalized_rows))

    print(f"Test cases: {len(rows)}")
    print(f"Duplicate rows: {duplicates}")
    print(f"Invalid values: {len(invalid_values)}")
    print(f"Pairwise coverage: {len(required) - len(missing)}/{len(required)}")
    for issue in invalid_values:
        print(f"INVALID: {issue}")
    for left, left_value, right, right_value in missing:
        print(f"MISSING: {left}={left_value!r}; {right}={right_value!r}")

    return 0 if not invalid_values and not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
