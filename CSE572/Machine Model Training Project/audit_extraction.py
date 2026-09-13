"""Audit extracted windows against raw records; does not retrain the model."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from train import (
    CARBS, GLUCOSE, PATIENT_FILES, extract_patient, extract_window,
    meal_starts, purge_overlaps, read_export,
)


def independent_read(path, column, patient):
    frame = pd.read_csv(path, low_memory=False)
    date_format = '%m/%d/%Y %H:%M:%S' if patient == 1 else '%Y-%m-%d %H:%M:%S'
    times = pd.to_datetime(frame.Date.str.strip().str.split().str[0] + ' ' + frame.Time, format=date_format)
    values = pd.to_numeric(frame[column], errors='coerce')
    series = pd.Series(values.to_numpy(), index=pd.DatetimeIndex(times)).sort_index()
    pd.testing.assert_series_equal(series, read_export(path, column))
    return series, len(frame), int(times.isna().sum())


def main():
    report = {'patients': {}, 'violations': [], 'examples': []}
    traces = []
    all_samples, all_y, all_groups, all_starts, all_patients, source_sets = [], [], [], [], [], []
    for patient, (cgm_file, insulin_file) in enumerate(PATIENT_FILES, 1):
        raw_cgm, cgm_rows, bad_cgm = independent_read(cgm_file, GLUCOSE, patient)
        insulin, insulin_rows, bad_insulin = independent_read(insulin_file, CARBS, patient)
        cgm = raw_cgm.groupby(level=0).mean().sort_index()
        events = insulin[insulin.notna() & insulin.ne(0)].index.unique().sort_values()
        # Independent forward chain walk for the PDF's later-meal rule.
        expected = []
        for time in events:
            if expected and time - expected[-1] <= pd.Timedelta(hours=2):
                expected[-1] = time
            else:
                expected.append(time)
        _, actual = meal_starts(insulin)
        assert expected == actual
        samples, labels, groups, starts, stats = extract_patient(cgm, insulin, patient)
        summary = {
            'raw_cgm_rows': cgm_rows, 'raw_insulin_rows': insulin_rows,
            'unparseable_timestamps': bad_cgm + bad_insulin,
            'duplicate_cgm_timestamps': len(raw_cgm) - len(cgm),
            'close_meal_gaps': int(((events[1:] - events[:-1]) < pd.Timedelta(hours=2)).sum()),
            'exact_two_hour_gaps': int(((events[1:] - events[:-1]) == pd.Timedelta(hours=2)).sum()),
            'extraction': stats,
            'windows_with_interpolation': {'meal': 0, 'no_meal': 0},
            'cross_label_shared_readings': 0,
        }
        by_label = {0: set(), 1: set()}
        offsets = []
        for sample, label, requested in zip(samples, labels, starts):
            start = pd.Timestamp(requested)
            end = start + pd.Timedelta(minutes=5 * len(sample))
            anchor = cgm.index[cgm.index.searchsorted(start)]
            grid = pd.date_range(anchor, periods=len(sample), freq='5min')
            interval = cgm[(cgm.index >= start) & (cgm.index < end)]
            positions = interval.index.get_indexer(grid, method='nearest', tolerance=pd.Timedelta(seconds=90))
            present = positions >= 0
            actual_times = interval.index[positions[present]]
            raw_values = np.full(len(sample), np.nan)
            raw_values[present] = interval.iloc[positions[present]].to_numpy()
            raw_values[~np.isfinite(raw_values) | (raw_values <= 0)] = np.nan
            np.testing.assert_equal(sample, raw_values)
            assert len(sample) == (30 if label else 24)
            offsets.append((anchor - start).total_seconds())
            if len(set(positions[present])) != present.sum():
                report['violations'].append([patient, requested, 'reused reading within window'])
            if (actual_times < start).any() or (actual_times >= end).any():
                report['violations'].append([patient, requested, 'reading outside requested interval'])
            if label:
                assert np.isfinite(sample).all() and (sample > 0).all()
                meal = start + pd.Timedelta(minutes=30)
                assert meal in expected
                assert not ((events > meal) & (events <= meal + pd.Timedelta(hours=2))).any()
            else:
                previous = events[events <= start]
                assert len(previous) and start - previous[-1] >= pd.Timedelta(hours=2)
                assert not ((events >= start) & (events < end)).any()
            missing = int(np.isnan(sample).sum())
            kind = 'meal' if label else 'no_meal'
            summary['windows_with_interpolation'][kind] += int(missing > 0)
            sources = {(patient, int(time.value)) for time in actual_times}
            by_label[label].update(sources)
            source_sets.append(sources)
            trace = {
                'patient': patient, 'label': label, 'requested_start': requested,
                'requested_end_exclusive': end.isoformat(),
                'first_actual_reading': actual_times[0].isoformat(),
                'last_actual_reading': actual_times[-1].isoformat(),
                'missing_values': missing, 'columns': len(sample),
                'preceding_or_current_meal': events[events <= (start + pd.Timedelta(minutes=30) if label else start)][-1].isoformat(),
            }
            traces.append(trace)
            if not any(e['patient'] == patient and e['label'] == label for e in report['examples']):
                report['examples'].append(trace)
        summary['anchor_delay_seconds'] = {'min': min(offsets), 'max': max(offsets)}
        summary['cross_label_shared_readings'] = len(by_label[0] & by_label[1])
        # Quantify the additional windows allowed if the baseline buffer is removed.
        kept_negative_starts = {pd.Timestamp(t) for t, y in zip(starts, labels) if y == 0}
        extra = []
        coverage_end = min(cgm.index[-1] + pd.Timedelta(minutes=5), insulin.index.max())
        for i, event in enumerate(events):
            end = min(events[i + 1], coverage_end) if i + 1 < len(events) else coverage_end
            start = event + pd.Timedelta(hours=2)
            while start + pd.Timedelta(hours=2) <= end:
                if start not in kept_negative_starts and extract_window(cgm, start, 24) is not None:
                    extra.append(start.isoformat())
                start += pd.Timedelta(hours=2)
        summary['additional_usable_no_meal_windows_without_baseline_buffer'] = len(extra)
        summary['additional_no_meal_examples'] = extra[:3]
        report['patients'][str(patient)] = summary
        all_samples.extend(samples)
        all_y.extend(labels)
        all_groups.extend(groups)
        all_starts.extend(starts)
        all_patients.extend([patient] * len(labels))

    patients = np.asarray(all_patients)
    report['validation_source_overlap'] = []
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=572)
    for fold, (training, validation) in enumerate(cv.split(np.zeros(len(all_y)), all_y, all_groups), 1):
        kept = purge_overlaps(training, validation, all_starts, all_samples, patients)
        train_sources = set().union(*(source_sets[i] for i in kept))
        validation_sources = set().union(*(source_sets[i] for i in validation))
        shared = len(train_sources & validation_sources)
        report['validation_source_overlap'].append({'fold': fold, 'purged_windows': len(training) - len(kept), 'shared_readings': shared})
        assert shared == 0
    pd.DataFrame(traces).to_csv('extraction_window_trace.csv', index=False)
    Path('extraction_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
