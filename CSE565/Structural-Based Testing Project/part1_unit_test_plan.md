# Part 1 Unit Test Plan

## File Under Test

`VendingMachine.java`

## Goal

The assignment goal is to reach:

- 100% statement coverage
- 90% decision coverage

## Test Cases

| Test | Input | Item | Expected Result | Coverage Purpose |
|---|---:|---|---|---|
| Constructor | n/a | n/a | Vending machine object is not null | Covers the implicit constructor counted as an executable line. |
| Candy with extra money | 30 | candy | `Item dispensed and change of 10 returned` | Covers candy cost branch and `input > cost` branch. |
| Coke exact money | 25 | coke | `Item dispensed.` | Covers coke cost branch and `input == cost` branch. |
| Coffee exact money | 45 | coffee | `Item dispensed.` | Covers coffee cost branch. |
| Coffee, enough for candy or coke | 30 | coffee | `Item not dispensed, missing 15 cents. Can purchase candy or coke.` | Covers insufficient-money branch where `input < 45` is true, but `input < 25` and `input < 20` are false. |
| Coffee, enough for candy only | 22 | coffee | `Item not dispensed, missing 23 cents. Can purchase candy.` | Covers insufficient-money branch where `input < 45` and `input < 25` are true, but `input < 20` is false. |
| Coffee, not enough for anything | 10 | coffee | `Item not dispensed, missing 35 cents. Cannot purchase item.` | Covers insufficient-money branch where `input < 45`, `input < 25`, and `input < 20` are all true. |

## Notes

The code compares strings using `==`, so these tests use string literals like `"candy"`, `"coke"`, and `"coffee"`. That makes the tests pass with the current implementation because Java interns string literals.

Using `new String("candy")` would likely expose a defect, because `==` compares object identity instead of string content. That is a useful discussion point, but it may not be necessary for coverage.

## How To Run The Current Harness

```bash
javac -cp ".:lib/*" VendingMachine.java VendingMachineTestHarness.java
java -javaagent:lib/jacocoagent.jar -cp ".:lib/*" VendingMachineTestHarness
```

Current result:

```text
Passed 7 of 7 tests.
Line coverage: 100.00% (24/24)
Decision coverage: 93.75% (15/16)
```

## Report Evidence

Include the test harness code from `VendingMachineTestHarness.java` in the report to show the test cases that were written.

Include `screenshots/output.png` in the report to show that the vending machine tests were executed successfully and printed coverage results.
