# AI Prompts For Unit Testing Project

## Prompt 1

```text
I wrote a Python Heapsort implementation for a software unit testing project.
The code defines a class named heap. To use it, create h = heap(input_list),
call h.heapify(), and then check h.arr for the sorted result.

Please generate Python unittest test cases for this Heapsort implementation.
Cover normal input and edge cases, including an empty list, one-element list,
already sorted list, reverse-sorted list, duplicate values, negative numbers,
mixed positive and negative numbers, and all equal values.
```

## AI-Generated Response 1

```python
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
```

## Execution Result 1

Summary:

- Test framework: Python `unittest`
- Test file: `test_heap_sort_ai.py`
- Tests run: 8
- Result: Passed
- Screenshot evidence: `screenshots/eight ai tests.png`

![AI-generated unit tests passed](screenshots/eight%20ai%20tests.png)

Command:

```bash
python3 -m unittest test_heap_sort_ai.py
```

Output:

```text
........
----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK
```
