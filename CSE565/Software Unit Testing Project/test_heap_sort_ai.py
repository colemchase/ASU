import unittest

from heap_sort import heap


class TestHeapSortAI(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
