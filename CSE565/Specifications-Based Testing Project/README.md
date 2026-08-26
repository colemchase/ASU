# CSE 565 - Specification-Based Testing Project

## Purpose

Specification-based black-box testing project using a supplied Java application/JAR and a spreadsheet for test cases and defect tracking.

The project focuses on:

- equivalence partitioning
- boundary value analysis
- cause-and-effect testing

The supplied JAR contains at least 10 seeded defects.

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

## Program Inputs

The command-line JAR takes seven arguments:

```text
<name> <age> <user status> <reward member status> <season bought> <product category> <rating>
```

Example:

```bash
java -jar CSE565P1.jar Peter 24 Returning Silver Spring Electronics 5
```

Accepted valid values:

- User Status: `New` or `Returning`
- Reward Member Status: `Bronze`, `Silver`, or `Gold`
- Season Bought: `Winter`, `Spring`, `Summer`, or `Fall`
- Product Category: `Unknown` or `Electronics`

The overview says not to test invalid partitions for user status, reward status, season, or product category.

## Requirements To Test

Input requirements:

- Requirement 1.1: user name must be 5-10 characters long.
- Requirement 1.2: user name can only contain letters, no numbers.
- Requirement 1.3: user name cannot contain a hyphen or underscore.
- Requirement 2.1: age must be 18 or over.
- Requirement 7.1: rating must be between 1 and 10.

Output/error requirements:

- Requirement 8: program should show error messages for incorrect username, age, and rating.

Discount requirements:

- Requirement 9.1: new users cannot receive discounts.
- Requirement 9.2: unknown product category receives no discount.
- Requirement 9.3.1: returning + gold + summer + electronics receives 15% discount voucher.
- Requirement 9.4.1: returning + bronze + spring + electronics receives 10% discount voucher.
- Requirement 9.5.1: returning + gold + winter + electronics receives 25% discount voucher.
- Requirement 9.6.1: returning + silver + fall + electronics receives 15% discount voucher.
- Requirement 9.7: any other returning-user combination receives no discount.

Important equivalence partitioning rule from the overview:

- Test only one invalid partition at a time.

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

- Extract the supplied ZIP.
- Build a complete set of spreadsheet test cases using equivalence partitioning, boundary value analysis, and cause/effect analysis.
- Execute each test case using the GUI, command line JAR, or provided script.
- Mark each test case as pass/fail in the spreadsheet.
- Highlight failed test cases red.
- Fill in the defect tracking sheet.
- Find and map at least 10 defects.

## Required Deliverable

Submit one Excel file:

```text
yourlastname_firstname_CSE 565_Specification-Based Testing Project
```

The workbook must include:

- completed test case matrix
- pass/fail results
- failed tests highlighted red
- defect tracking sheet with defect number, description, requirement mapping, and test case mapping

## Notes For Future Codex

- The spreadsheet filename contains a typo: `Spreatsheet`.
- The PDF text was extracted manually from embedded PDF glyph maps because standard PDF text tools were unavailable.
