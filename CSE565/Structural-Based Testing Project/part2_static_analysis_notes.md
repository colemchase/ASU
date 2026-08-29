# Part 2 Static Analysis Notes

## Tool Used

PMD 6.55.0 was used as the static source code analysis tool.

PMD analyzes source code without executing it. It can detect code quality issues, possible defects, unused variables, suspicious comparisons, style issues, and design problems.

## Command Used

```bash
/tmp/pmd-bin-6.55.0/bin/run.sh pmd -d StaticAnalysis.java -R rulesets/java/quickstart.xml -f text > pmd_static_analysis_report.txt
```

PMD returned exit code `4`, which means violations were found. This is expected for this assignment.

## Findings

PMD reported these issues in `StaticAnalysis.java`:

| Line | PMD Rule | Finding |
|---:|---|---|
| 4 | `NoPackage` | The class does not belong to a named package. |
| 5 | `UseUtilityClass` | The class contains all static methods and could be treated as a utility class. |
| 15 | `UnusedLocalVariable` | The local variable `weight` is assigned but never used. |
| 16 | `UnusedLocalVariable` | The local variable `length` is assigned but never used. |
| 24 | `CompareObjectsWithEquals` | The code compares object references instead of using `.equals()`. |
| 24 | `UseEqualsToCompareStrings` | The code compares strings using `==` instead of `.equals()`. |
| 34 | `ControlStatementBraces` | The `if` statement body does not use braces. |
| 36 | `ControlStatementBraces` | The `else` statement body does not use braces. |

## Built-In Anomalies Identified

PMD successfully identified the unused local variables in the constructor:

```java
int weight = 0;
String length = "";
```

These variables are assigned values but are never used. This is a data flow anomaly because the variables are defined without being used.

PMD also identified the suspicious string comparison:

```java
if(product == "Electronics")
```

In Java, strings should usually be compared with `.equals()` because `==` compares object references, not string contents. A safer version would be:

```java
if ("Electronics".equals(product))
```

## Tool Performance

PMD performed well on this file because it identified the main built-in anomalies: the unused variables and the incorrect string comparison. It also reported additional code quality findings, including missing braces and lack of a package declaration.

Some PMD findings are style or design recommendations rather than functional defects. For example, `NoPackage`, `UseUtilityClass`, and `ControlStatementBraces` do not necessarily mean the program is incorrect. They are still useful because they improve maintainability and reduce risk.

## Assessment

PMD was easy to use because it can be run from the command line with a ruleset and source file. The text report is readable and includes line numbers, rule names, and descriptions.

PMD covers many anomaly types, including unused variables, questionable object comparisons, empty code blocks, duplicate code, overly complex methods, and style/design issues. For this assignment, its most useful findings were the unused local variables and the string comparison warning.
