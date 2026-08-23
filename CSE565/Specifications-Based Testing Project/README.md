# CSE 565 - Specification-Based Testing Project

## Purpose

Specification-based testing project using a supplied Java application/JAR and a spreadsheet for test cases and defect tracking.

## Files

- `CSE 565_Specification-Based Testing Project_Overview Document.pdf` - assignment overview document.
- `CSE 565_Specification-Based Testing Project_JAR Files and Script.zip` - supplied executable artifacts.
- `CSE 565_Specification-Based Testing Project_Test Case and Defect Spreatsheet.xlsx` - test case and defect tracking workbook.

## ZIP Contents

The supplied ZIP contains:

- `Jar Files and Project1Script/CSE565P1.jar`
- `Jar Files and Project1Script/project1GUI.jar`
- `Jar Files and Project1Script/Project1Script`
- macOS metadata under `__MACOSX/`

## Spreadsheet Structure

Workbook sheets:

- `Test Case Matrix`
- `Defect Tracking `

`Test Case Matrix` columns:

- `Valid/Invalid`
- `Test Case Number`
- `Name`
- `Age`
- `User Status`
- `Reward Member Status`
- `Season Bought`
- `Product Category`
- `Rating`
- `Pass/Fail`
- `Requirements Mapping`

Example row currently present:

- Invalid, Test Case #1, Name `M1234`, Age `18`, New user, Bronze reward member, Winter, Unknown category, Rating `1`, expected/pass note `Pass digits`, mapped to `1-7, 8, 9.1, 9.2`

`Defect Tracking` columns:

- `Defect Number`
- `Defect Description`
- `Requirement Mapping`
- `Test Cases Mapping`

Example defect row currently present:

- `D1`, placeholder description for expected vs observed behavior, requirement mapping `1.1`, mapped to `Test Case #1`

## What To Do Next

- Read the overview PDF for the system specification and required input partitions/boundary cases.
- Run the provided JAR/script to execute test cases.
- Fill in the test matrix and defect tracking sheet based on observed results.

## Notes For Future Codex

- The spreadsheet filename contains a typo: `Spreatsheet`.
- Local PDF text extraction tools were not available when this README was created, so exact requirements must be read from the PDF.
