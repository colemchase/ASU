# CSE 565: Software Verification and Validation

## Structural-Based Testing Project

## Purpose

The goal of this project is to explore and analyze code coverage using structural-based testing techniques.

## Objectives

Learners will be able to:

- Analyze code coverage using statement and decision coverage techniques.
- Develop a set of test cases based on specified requirements.
- Learn about different data flow anomalies.

## Technology Requirements

- Java 17 or above

## Project Description

This assignment focuses on two aspects of software testing and code analysis.

Part 1 explores code coverage analysis for a vending machine application. The goal is to assess code coverage using statement and decision coverage techniques, identify untested areas, and improve the test suite.

Part 2 focuses on data flow analysis in static analysis code. The goal is to detect data flow anomalies, such as data leaks and uninitialized variables.

## Provided Files

- `VendingMachine.java`
- `StaticAnalysis.java`

The original PDF refers to `StatisticAnalysis.java`, but the local project folder contains `StaticAnalysis.java`.

## Part 1: Code Coverage Analysis

Research and experiment with a tool that provides statement and decision code coverage.

Use `VendingMachine.java` and develop test cases based on these requirements:

- Takes in an integer input.
- Allows users to select between three products:
  - Candy: 20 cents
  - Coke: 25 cents
  - Coffee: 45 cents
- Returns the selected product and any remaining change.
- If there is not enough money to buy the product, displays the amount necessary to buy the product and other products the user can purchase.

Execute the program with the test cases, observe the code coverage, and report the code coverage achieved.

Coverage goals:

- 100% statement coverage.
- 90% decision coverage.

Test cases should be changed until the desired coverage is reached.

## Part 2: Static Source Code Analysis

Research and experiment with a static source code analysis tool.

Use `StaticAnalysis.java`, which contains two different data flow anomalies.

The inputs to this code are:

- Package weight as an integer.
- Package length as an integer.
- Product type as a string.

Execute the selected static analysis tool and analyze the report generated for `StaticAnalysis.java`.

Analyze the findings and comment on how well the tool performed in identifying the two built-in anomalies.

Assess the tool in your own words in terms of:

- Features and functionalities provided by the tool.
- Type of anomalies covered by the tool.
- Ease of use.

## Submission Directions

Submit one PDF report to the course submission space.

Title the file:

```text
yourlastname_firstname_CSE 565_Structural-Based Testing Project
```

The report should be in APA or MLA style and include Part 1 and Part 2, with screenshots of test cases, coverage, and detailed explanations of what the screenshots represent.

## Report Requirements

### Part 1

Include:

1. A description of the tool used and the type of code coverage it provides.
2. A description of the test cases developed, including screenshots of the code written.
3. A report and discussion of the coverage achieved for the test cases executed, including screenshots showing the tool's coverage.

### Part 2

Include:

1. A description of the static source code analysis tool used.
2. The static analysis report or screenshots of the report.
3. An analysis of the tool's findings on `StaticAnalysis.java`.
4. Comments on how well the tool identified the two built-in anomalies.
5. An assessment of the tool's features, anomaly coverage, and ease of use.
