"""Local regression checks; only train.py and test.py are submitted to Ed."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from train import extract_patient, extract_window, meal_starts, purge_overlaps
from test import FEATURE_NAMES, extract_features, load_model, predict_sample


class ProjectChecks(unittest.TestCase):
    def setUp(self):
        self.start = pd.Timestamp('2020-01-01 09:00')
        self.cgm = pd.Series(100.0, index=pd.date_range(self.start - pd.Timedelta(hours=1), periods=180, freq='5min'))

    def test_close_and_exact_two_hour_meals(self):
        events = pd.to_datetime(['2020-01-01 09:00', '2020-01-01 10:00', '2020-01-01 12:00', '2020-01-01 16:00'])
        insulin = pd.Series([10, 20, 30, 40], index=events)
        all_events, accepted = meal_starts(insulin)
        self.assertEqual(len(all_events), 4)
        self.assertEqual(accepted, list(events[2:]))
        samples, labels, _, starts, _ = extract_patient(self.cgm, insulin, 1)
        meal_times = [t for t, y in zip(starts, labels) if y == 1]
        self.assertEqual(meal_times, ['2020-01-01T11:30:00', '2020-01-01T15:30:00'])
        self.assertTrue(all(len(x) == (30 if y else 24) for x, y in zip(samples, labels)))

    def test_zero_carbs_do_not_interrupt_no_meal(self):
        insulin = pd.Series([30, 0, np.nan, 40], index=pd.to_datetime([
            '2020-01-01 09:00', '2020-01-01 12:00', '2020-01-01 14:00', '2020-01-01 16:00']))
        _, labels, _, starts, _ = extract_patient(self.cgm, insulin, 1)
        negatives = [t for t, y in zip(starts, labels) if y == 0]
        self.assertEqual(negatives, ['2020-01-01T11:00:00', '2020-01-01T13:00:00'])

    def test_missing_timestamps_preserve_positions(self):
        cgm = self.cgm.drop(self.start + pd.Timedelta(minutes=10))
        x = extract_window(cgm, self.start, 24)
        self.assertEqual(len(x), 24)
        self.assertTrue(np.isnan(x[2]))
        self.assertTrue(np.isfinite(extract_features([x])).all())
        broken = self.cgm.drop(pd.date_range(self.start + pd.Timedelta(minutes=10), periods=3, freq='5min'))
        self.assertIsNone(extract_window(broken, self.start, 24))
        self.assertIsNone(extract_window(self.cgm, self.cgm.index[-1], 24))

    def test_constant_and_variable_length_features(self):
        features = extract_features([np.full(24, 100), np.full(30, 100)])
        self.assertEqual(features.shape, (2, len(FEATURE_NAMES)))
        self.assertTrue(np.isfinite(features).all())
        np.testing.assert_allclose(features[0], features[1])

    def test_overlap_purge(self):
        samples = [np.ones(30), np.ones(24), np.ones(24), np.ones(24)]
        starts = ['2020-01-05 23:00', '2020-01-06 00:00', '2020-01-06 06:00', '2020-01-06 00:00']
        kept = purge_overlaps(np.array([0, 2, 3]), np.array([1]), starts, samples, np.array([1, 1, 1, 2]))
        self.assertEqual(kept.tolist(), [2, 3])

    def test_prediction_contract_in_fresh_process(self):
        model = load_model()
        rows = np.stack([np.full(24, 100), np.linspace(90, 220, 24), np.full(24, np.nan)])
        rows[0, 5] = np.nan
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, result = root / 'test.csv', root / 'Result.csv'
            np.savetxt(source, rows, delimiter=',')
            subprocess.run([sys.executable, 'test.py', '--input', str(source), '--output', str(result)], check=True, capture_output=True)
            lines = result.read_text().splitlines()
            self.assertEqual(len(lines), len(rows))
            self.assertTrue(all(line in ('0', '1') for line in lines))
            self.assertEqual([int(line) for line in lines], [predict_sample(x, model) for x in rows])
            np.savetxt(source, rows[:1], delimiter=',')
            subprocess.run([sys.executable, 'test.py', '--input', str(source), '--output', str(result)], check=True, capture_output=True)
            self.assertEqual(len(result.read_text().splitlines()), 1)
            source.write_text('')
            subprocess.run([sys.executable, 'test.py', '--input', str(source), '--output', str(result)], check=True, capture_output=True)
            self.assertEqual(result.read_text(), '')
            np.savetxt(source, np.ones((2, 23)), delimiter=',')
            invalid = subprocess.run([sys.executable, 'test.py', '--input', str(source), '--output', str(result)], capture_output=True)
            self.assertNotEqual(invalid.returncode, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
