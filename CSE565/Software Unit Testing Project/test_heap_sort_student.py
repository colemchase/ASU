import random
import unittest

from heap_sort import heap


class TestHeapSortStudent(unittest.TestCase):
    def run_heap_sort(self, values):
        h = heap(values)
        h.heapify()
        return h.arr

    def test_empty_list(self):
        self.assertEqual(self.run_heap_sort([]), [])
    
    def test_single_element_list(self):
        self.assertEqual(self.run_heap_sort([5]), [5])

    def test_already_sorted_list(self):
        self.assertEqual(self.run_heap_sort([1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])

    def test_reverse_sorted_list(self):
        self.assertEqual(self.run_heap_sort([5, 4, 3, 2, 1]), [1, 2, 3, 4, 5])

    def test_duplicate_values(self):
        self.assertEqual(self.run_heap_sort([4, 1, 3, 4, 2, 1]), [1, 1, 2, 3, 4, 4])

    def test_negative_numbers(self):
        self.assertEqual(self.run_heap_sort([-3, -1, -7, -2]), [-7, -3, -2, -1])

    def test_mixed_positive_and_negative_numbers(self):
        self.assertEqual(self.run_heap_sort([3, -1, 0, -5, 8]), [-5, -1, 0, 3, 8])

    def test_all_equal_values(self):
        self.assertEqual(self.run_heap_sort([2, 2, 2, 2]), [2, 2, 2, 2])

    def test_float_list(self):
        self.assertEqual(self.run_heap_sort([3, 4, 1, 0.0]), [0.0, 1, 3, 4])

    def test_random_element_list(self):
        self.assertEqual(self.run_heap_sort([14, 12, 13, 15, 5, 6 ,7, 9, 8, 10, 11, 4, 3, 2, 1]), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

    def test_original_input_is_not_changed(self):
        values = [4, 1, 3, 2]
        original = list(values)

        self.run_heap_sort(values)

        self.assertEqual(values, original)

    def test_mixed_float_negative_and_duplicate_values(self):
        values = [2.5, -1.0, 2.5, 0, -3.25, 8]
        self.assertEqual(self.run_heap_sort(values), [-3.25, -1.0, 0, 2.5, 2.5, 8])

    def test_large_reverse_sorted_list(self):
        values = list(range(100, 0, -1))
        self.assertEqual(self.run_heap_sort(values), list(range(1, 101)))

    def test_random_lists_match_python_sorted(self):
        random.seed(565)

        for _ in range(20):
            values = [random.randint(-100, 100) for _ in range(25)]
            self.assertEqual(self.run_heap_sort(values), sorted(values))


if __name__ == "__main__":
    unittest.main()
