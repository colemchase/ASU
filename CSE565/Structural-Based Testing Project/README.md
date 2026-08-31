# CSE 565 - Structural-Based Testing Project

## Purpose

Structural/white-box testing project. The folder includes Java programs suitable for static analysis, control-flow analysis, path testing, branch coverage, and unit test design. All Done

## Files

- `CSE 565_Structural-Based Testing Project_Overview Document.pdf` - assignment overview document.
- `VendingMachine.java` - vending machine logic to test.
- `StaticAnalysis.java` - small Java program intended for static analysis.

## `VendingMachine.java`

Main method under test:

```java
public static String dispenseItem(int input, String item)
```

Behavior:

- Sets item cost based on the requested item:
  - `candy` costs 20
  - `coke` costs 25
  - `coffee` costs 45
- If `input > cost`, returns item dispensed plus change.
- If `input == cost`, returns item dispensed.
- If `input < cost`, returns a missing-cents message and a note about what the user can afford.

Important testing/static-analysis notes:

- Uses `==` for Java string comparison instead of `.equals(...)`; this can fail for non-interned strings.
- Unknown item names leave `cost = 0`, which can cause nonsensical successful dispense behavior for positive input.
- The insufficient-funds messages are controlled only by `input` thresholds, not by the selected item. This can produce odd recommendations.
- Multiple independent `if` statements overwrite `returnValue` for lower inputs.

## `StaticAnalysis.java`

Contains:

- `main`, which calls `calculateCost(5, 10, "Electronics")` and `calculateCost(2, 3, "Clothing")`.
- Constructor with local variables `weight` and `length` that are assigned but unused.
- `calculateCost(int weight, int length, String product)`.

Important testing/static-analysis notes:

- Uses `==` for Java string comparison instead of `.equals(...)`.
- `calculateCost` doubles cost for `Electronics`; otherwise cost is `weight * length`.
- If `cost < 15`, output says flat rate `$10.00`; otherwise output reports the computed cost.
- The first call in `main` discards the return value.
- Constructor local variables are unused and do not affect object state.

## What To Do Next

- Read the overview PDF for exact coverage criteria and report expectations.
- Likely deliverables include static-analysis findings, control-flow/path analysis, test cases, expected results, and possibly JUnit tests.

## Notes For Future Codex

- Local PDF text extraction tools were not available when this README was created, so exact rubric details should be checked in the overview PDF.
