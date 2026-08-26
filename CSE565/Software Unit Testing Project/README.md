# CSE 565 - Software Unit Testing Framework Project

## Purpose

Course project for demonstrating unit-level testing, use of a unit testing framework, generation of test cases with a generative AI tool, and critical assessment of the AI-generated tests.

The required algorithm is Heapsort.

## Files

- `CSE 565_Software Unit Testing Framework Project_Overview Document.pdf` - assignment overview document.
- `heap_sort.py` - Python Heapsort implementation for Task 1.
- `ai_prompts.md` - prompt, generated unit tests, and execution result for the AI-generated test step.
- `test_heap_sort_ai.py` - AI-generated `unittest` test cases.

## Assignment Tasks

1. Download or write code that implements the Heapsort algorithm.
   - Allowed languages: Java, C++, Python, or JavaScript.
2. Choose a unit testing framework for the selected language.
   - Use a generative AI tool to create unit-level test cases for the Heapsort implementation.
   - Record the prompts used and the AI-generated results.
3. Execute the generated tests in an IDE.
   - Report test outputs.
   - Include screenshots showing execution and results.
4. Assess the validity and adequacy of the AI-generated tests.
   - Identify missing or weak cases.
   - Improve/update the test cases.
   - Execute the updated tests and include evidence.
5. Assess the generative AI tool.
   - Describe the experience of using it.
   - Evaluate how well it generated unit-level test cases using the chosen framework.

## Required Deliverable

Submit one PDF report named:

```text
yourlastname_firstname_CSE 565_UnitTestingProject
```

The report must contain:

- screenshot of the Heapsort code
- explanation of the chosen unit testing framework
- explanation of the chosen generative AI tool
- screenshots of prompts used to generate tests
- screenshots/results of AI-generated test cases
- screenshots/results from executing the AI-generated tests
- assessment of validity and weaknesses of those tests
- student-improved test cases and execution results
- assessment of the generative AI tool's effectiveness

## Recommended Implementation Plan

- Use Python with `pytest` unless there is a reason to prefer another language.
- Create `heap_sort.py` with a small, readable Heapsort implementation. Done.
- Use Python's built-in `unittest` framework to avoid extra dependencies. Done.
- Ask the AI tool to generate tests for the function. Done.
- Save the exact prompts and responses in `ai_prompts.md`. Done.
- Run the generated tests and capture output. Done.
- Add stronger tests for edge cases and mutation-style defects.
- Write the PDF report after code and tests are stable.

## Test Cases To Make Sure We Cover

- empty list
- one-element list
- already sorted list
- reverse-sorted list
- duplicate values
- negative numbers
- mixed positive/negative numbers
- all equal values
- large unsorted list
- input mutation behavior, if the implementation sorts in place
- comparison against Python's built-in `sorted`

## Likely Project Files To Create

- `heap_sort.py` - created
- `test_heap_sort_ai.py` - created
- `test_heap_sort_improved.py`
- `ai_prompts.md` - created
- final PDF report

## Notes For Future Codex

- `heap_sort.py` returns a sorted copy of the input instead of sorting in place.
- `pytest` was not installed locally when Step 1 was completed; use either `pytest` after installing it or Python's built-in `unittest`.
- The PDF text was extracted manually from embedded PDF glyph maps because standard PDF text tools were unavailable.
- The PDF footer appears to say "Design of Experiments Assignment" on some pages, but the actual document title and content are for the Software Unit Testing Framework Project.
