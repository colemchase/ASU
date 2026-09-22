# CSE 565 - Design of Experiments Project Plan

## Goal

Create and assess two independent pairwise Design of Experiments (DOE) test suites for the specified mobile application:

1. A suite generated with a dedicated DOE tool.
2. A suite generated with a generative AI tool (ChatGPT).

The final deliverable is one polished PDF report containing evidence, test suites, validation results, comparison, and tool assessments.

## Assignment Requirements

The report must contain:

1. An explanation of the DOE-tool-generated test cases, including screenshots of the tool and results.
2. An explanation of the generative-AI-generated test cases, including the exact prompt, result, and screenshots.
3. An assessment of both suites' validity and alignment with pairwise DOE guidelines.
4. An assessment of the DOE tool: features/functionality, scope, performance, and ease of use.
5. An assessment of the AI tool: prompt/result experience and the significance of generative AI in DOE-based testing.

## System Under Test: Factors and Levels

| Factor | Levels | Count |
|---|---|---:|
| Type of Phone | iPhone 14; iPhone 13; Galaxy Z; Huawei Mate; Google Pixel 7 | 5 |
| Authentication | Fingerprint; Face recognition; Text Password | 3 |
| Connectivity | Wireless; 3G; 4G LTE; 5G Edge | 4 |
| Memory | 128 GB; 256 GB; 512 GB; 1 TB | 4 |
| Battery Level | < 20%; 20-39%; 40-59%; 60-79%; 80-100% | 5 |

There are `5 x 3 x 4 x 4 x 5 = 1,200` exhaustive input combinations. The project uses pairwise coverage instead: every value-pair across every two factors must occur in at least one test case.

The model has 175 required value-pairs across its 10 factor-pairs:

| Factor Pair | Required Value-Pairs |
|---|---:|
| Phone x Authentication | 15 |
| Phone x Connectivity | 20 |
| Phone x Memory | 20 |
| Phone x Battery | 25 |
| Authentication x Connectivity | 12 |
| Authentication x Memory | 12 |
| Authentication x Battery | 15 |
| Connectivity x Memory | 16 |
| Connectivity x Battery | 20 |
| Memory x Battery | 20 |
| **Total** | **175** |

## Tool Choices

### DOE tool: Microsoft PICT

PICT (Pairwise Independent Combinatorial Testing) will be used as the dedicated DOE tool. It accepts a plain-text parameter model and generates pairwise test cases by default. Its command-line workflow also makes the model and output reproducible.

### Generative AI tool: ChatGPT

ChatGPT will independently produce a pairwise suite from a structured prompt. The exact prompt and unedited result will be preserved as report evidence.

## Execution Plan

### Phase 1 - Prepare the DOE model

- [x] Create a PICT model containing exactly the five required factors and allowed levels.
- [x] Check spelling, punctuation, and level counts against the assignment specification.
- [x] Keep the model under version control / in the project folder for reproducibility.

### Phase 2 - Generate the DOE-tool suite

- [x] Install or access PICT.
- [x] Run PICT with default pairwise strength (2-way).
- [x] Save the raw output as a CSV or text file.
- [x] Record the command, tool version, model, suite size, and generation time.
- [ ] Capture screenshots showing the model/command and generated output.

### Phase 3 - Generate the AI suite

- [x] Use a prompt that supplies all factors and levels verbatim.
- [x] Require a complete, rectangular CSV/Markdown table with one test case per row.
- [x] Require pairwise coverage, only valid values, and no explanatory text inside the data table.
- [x] Save the exact prompt and full unedited AI response.
- [ ] Capture screenshots of both the prompt and the output.

### Phase 4 - Verify both suites independently

Use a verification script rather than relying on either tool's claim of coverage.

- [x] Confirm every row has five factor values.
- [x] Confirm every value belongs to its factor's permitted level set.
- [x] Count test cases and identify duplicate rows.
- [x] Enumerate all 175 required pairs.
- [x] Report coverage as `covered / 175` and list any missing pairs.
- [x] Confirm both suites achieve 175/175 pair coverage before using them in the report.

### Phase 5 - Analyze and compare

Compare the two suites on:

- [ ] Pairwise coverage and validity.
- [ ] Number of test cases (smaller is preferable only when full coverage is retained).
- [ ] Duplicate or invalid rows.
- [ ] Reproducibility and determinism.
- [ ] Time and effort required.
- [ ] Transparency of the generation method.
- [ ] Ease of modifying the model when requirements change.
- [ ] Prompt-engineering and manual cleanup needed for the AI result.

### Phase 6 - Write required tool assessments

#### PICT assessment

- [ ] Features and functionality.
- [ ] Scope covered by the tool.
- [ ] Performance and generated-suite quality.
- [ ] Ease of use, setup, model syntax, and reproducibility.

#### ChatGPT assessment

- [ ] Experience writing prompts and processing results.
- [ ] Accuracy, clarity, and any manual validation needed.
- [ ] Significance and limitations of generative AI for DOE testing.
- [ ] Comparison with a deterministic DOE tool.

### Phase 7 - Build and quality-check the final report

- [ ] Add title page and brief DOE/pairwise-testing introduction.
- [ ] Include the system specification and factor/level table.
- [ ] Include PICT evidence, its suite, and verification results.
- [ ] Include the ChatGPT prompt, evidence, suite, and verification results.
- [ ] Include a side-by-side comparison table and narrative analysis.
- [ ] Include both required tool assessments and a clear conclusion.
- [ ] Export to PDF using the required filename format: `Coleman_Chase_CSE 565_Design of Experiments Project.pdf`.
- [ ] Render and visually inspect every PDF page for readability, table overflow, complete screenshots, and correct page breaks.

## Definition of Done

The project is complete only when:

- Both suites contain only valid, complete test cases.
- Independent verification reports full `175/175` pair coverage for each suite.
- The report includes screenshots for PICT and ChatGPT, plus the exact AI prompt/result.
- All five required report sections are addressed.
- The final PDF is visually reviewed and ready to submit.

## Reference

- Assignment overview: `CSE 565_Design of Experiments Project_Overview Document.pdf`
- Microsoft PICT documentation: <https://github.com/microsoft/pict/blob/main/doc/pict.md>
