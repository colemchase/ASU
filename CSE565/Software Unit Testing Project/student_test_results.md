# Student-Improved Unit Test Results

## Purpose

These tests were added after reviewing the AI-generated unit tests. The AI-generated tests covered basic Heapsort cases, but the student-improved tests add stronger evidence that the implementation works correctly.

## What Was Improved

- Added a test confirming the original input list is not changed.
- Added a larger reverse-sorted list test.
- Added mixed float, negative, and duplicate values.
- Added randomized tests that compare the Heapsort result against Python's built-in `sorted`.
- Kept the student-added float list and larger shuffled integer list tests.

## Execution Summary

- Test framework: Python `unittest`
- Test file: `test_heap_sort_student.py`
- Tests run: 14
- Result: Passed
- Screenshot evidence: `screenshots/student added tests.png`

![Student-improved unit tests passed](screenshots/student%20added%20tests.png)

## Command

```bash
python3 -m unittest -v test_heap_sort_student.py
```

## Output

```text
test_all_equal_values (test_heap_sort_student.TestHeapSortStudent.test_all_equal_values) ... ok
test_already_sorted_list (test_heap_sort_student.TestHeapSortStudent.test_already_sorted_list) ... ok
test_duplicate_values (test_heap_sort_student.TestHeapSortStudent.test_duplicate_values) ... ok
test_empty_list (test_heap_sort_student.TestHeapSortStudent.test_empty_list) ... ok
test_float_list (test_heap_sort_student.TestHeapSortStudent.test_float_list) ... ok
test_large_reverse_sorted_list (test_heap_sort_student.TestHeapSortStudent.test_large_reverse_sorted_list) ... ok
test_mixed_float_negative_and_duplicate_values (test_heap_sort_student.TestHeapSortStudent.test_mixed_float_negative_and_duplicate_values) ... ok
test_mixed_positive_and_negative_numbers (test_heap_sort_student.TestHeapSortStudent.test_mixed_positive_and_negative_numbers) ... ok
test_negative_numbers (test_heap_sort_student.TestHeapSortStudent.test_negative_numbers) ... ok
test_original_input_is_not_changed (test_heap_sort_student.TestHeapSortStudent.test_original_input_is_not_changed) ... ok
test_random_element_list (test_heap_sort_student.TestHeapSortStudent.test_random_element_list) ... ok
test_random_lists_match_python_sorted (test_heap_sort_student.TestHeapSortStudent.test_random_lists_match_python_sorted) ... ok
test_reverse_sorted_list (test_heap_sort_student.TestHeapSortStudent.test_reverse_sorted_list) ... ok
test_single_element_list (test_heap_sort_student.TestHeapSortStudent.test_single_element_list) ... ok

----------------------------------------------------------------------
Ran 14 tests in 0.001s

OK
```

## Assessment

The AI-generated tests were a good starting point because they checked common sorting cases such as empty lists, duplicates, negative numbers, and reverse-sorted input. However, they did not verify whether the original input list was preserved, did not use randomized checks, and did not compare many generated inputs against a known correct sorting function.

The student-improved tests provide stronger confidence because they test more varied inputs and check the implementation against Python's built-in `sorted` function across multiple random lists.
