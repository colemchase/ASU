# Valid Passing Case Notes

This file is a working note for the CSE 565 Specifications-Based Testing Project.
It separates every valid discount combination that the JAR passes from the smaller
set that should stay in the submission spreadsheet.

## Key Finding

Using valid inputs only, the JAR has 19 discount-rule combinations that match the
expected output. It also has valid combinations that fail because of defects, most
notably every `New` user case, which should receive no discount but returns 10%.

Because the assignment penalizes unnecessary test cases, the spreadsheet should
not include all 19 passing combinations. It should include enough passing cases to
cover the valid input partitions and the discount rules that actually pass, plus
the 10 failing defect cases.

## Passing Cases Kept In The Spreadsheet

| Test Case | Purpose | Input Summary | Expected / Actual |
| --- | --- | --- | --- |
| #11 | Valid username lower boundary and main passing discount | `Chase 24 Returning Gold Summer Electronics 5` | 15% |
| #12 | Valid username upper boundary | `Alexandria 24 Returning Gold Summer Electronics 5` | 15% |
| #13 | Valid age boundary | `Peter 18 Returning Gold Summer Electronics 5` | 15% |
| #14 | Valid rating lower boundary | `Peter 24 Returning Gold Summer Electronics 1` | 15% |
| #15 | Valid rating upper boundary | `Peter 24 Returning Gold Summer Electronics 10` | 15% |
| #16 | Valid Unknown product with no discount | `Peter 24 Returning Gold Summer Unknown 5` | No discount |
| #17 | Valid Silver reward status and all-other returning rule | `Peter 24 Returning Silver Summer Electronics 5` | No discount |
| #18 | Valid Bronze reward status and Winter season | `Peter 24 Returning Bronze Winter Electronics 5` | No discount |
| #19 | Valid Spring season and all-other returning rule | `Peter 24 Returning Gold Spring Electronics 5` | No discount |
| #20 | Valid Fall season and all-other returning rule | `Peter 24 Returning Bronze Fall Electronics 5` | No discount |

## Valid Passing Discount Combinations Found

These are all valid discount combinations where the program output matched the
expected output when using `Peter 24 <status> <reward> <season> <category> 5`.

| Status | Reward | Season | Product | Expected / Actual |
| --- | --- | --- | --- | --- |
| Returning | Bronze | Winter | Unknown | No discount |
| Returning | Bronze | Winter | Electronics | No discount |
| Returning | Bronze | Spring | Unknown | No discount |
| Returning | Bronze | Summer | Unknown | No discount |
| Returning | Bronze | Summer | Electronics | No discount |
| Returning | Bronze | Fall | Unknown | No discount |
| Returning | Bronze | Fall | Electronics | No discount |
| Returning | Silver | Winter | Unknown | No discount |
| Returning | Silver | Winter | Electronics | No discount |
| Returning | Silver | Spring | Unknown | No discount |
| Returning | Silver | Spring | Electronics | No discount |
| Returning | Silver | Summer | Electronics | No discount |
| Returning | Silver | Fall | Unknown | No discount |
| Returning | Gold | Winter | Unknown | No discount |
| Returning | Gold | Spring | Unknown | No discount |
| Returning | Gold | Spring | Electronics | No discount |
| Returning | Gold | Summer | Unknown | No discount |
| Returning | Gold | Summer | Electronics | 15% |
| Returning | Gold | Fall | Unknown | No discount |

## Valid Requirements Without Passing Cases

Some valid requirements are covered by failing defect cases because the program is
wrong for those requirements:

| Requirement Area | Why There Is No Passing Case |
| --- | --- |
| New user no-discount rule | Every valid `New` user combination tested returned 10% instead of no discount. |
| Bronze + Spring + Electronics discount | Expected 10%, but the JAR returned 5%. |
| Gold + Winter + Electronics discount | Expected 25%, but the JAR returned 20%. |
| Silver + Fall + Electronics discount | Expected 15%, but the JAR returned 10%. |
| Returning + Gold + Fall + Electronics no-discount rule | Expected no discount, but the JAR returned 10%. |
| Silver + Summer + Unknown no-discount rule | Expected no discount, but the JAR returned 10%. |
