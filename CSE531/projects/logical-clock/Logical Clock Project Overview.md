# CSE 531: Distributed and Multiprocessor Operating Systems

# Logical Clock Project

## Purpose

The goal of this project is to implement Lamport's logical clock algorithm upon the gRPC Project. As shown in Diagram A, the processes use logical clocks and follow Lamport's algorithm to coordinate.

## Objectives

Learners will be able to:

- Determine the problem statement.
- Identify the goal of the problem statement.
- List relevant technologies for the setup and their versions.
- Explain the implementation processes.
- Explain implementation results.
- Implement Lamport's logical clock algorithm.
- Implement interconnected sub-interfaces in the correct location.
- Execute the specific order of interconnected sub-interfaces.

## Technology Requirements

- Access to GitHub
- Python
- gRPC
- You are required to use the files in the **Projects Overview and Resources** page in the **Welcome and Start Here** module of the course.

### Required Library Versions

| Library | Required version |
| --- | --- |
| `grpcio` | `1.71.2` |
| `grpcio-tools` | `1.71.2` |
| `protobuf` | `5.29.6` |

These are version requirements for libraries.

## Part 1: Written Report

Your written report must be a single PDF with the correct naming convention:

`CSE 531_Your Name_Logical Clock_Written Report`

Using the provided `Learner Template_CSE 531_Your Name_Logical Clock_Written Report`, compose a report addressing the following questions:

1. What is the problem statement and goal?
2. What is the goal of the problem statement?
3. What are the relevant technologies for the setup and their versions?
4. What are the implementation processes?
5. What are the results and their justifications?

Learners may add subheadings on the template to purposefully call attention to specific, organized details.

## Part 2: Project Code

### Major Tasks

1. Implement logical clock in every customer and branch process.
2. Implement Lamport's algorithm for clock coordination among the processes.

## Sample Expected Output

The following sample shows the event log for each branch. The `logical_clock` records the Lamport time assigned to that event.

```json
[
  {
    "id": 1,
    "type": "branch",
    "events": [
      {"customer-request-id": 1, "logical_clock": 2, "interface": "deposit", "comment": "event_recv from customer 1"},
      {"customer-request-id": 1, "logical_clock": 3, "interface": "propogate_deposit", "comment": "event_sent to branch 2"},
      {"customer-request-id": 1, "logical_clock": 4, "interface": "propogate_deposit", "comment": "event_sent to branch 3"},
      {"customer-request-id": 3, "logical_clock": 7, "interface": "propogate_deposit", "comment": "event_recv from branch 2"},
      {"customer-request-id": 5, "logical_clock": 8, "interface": "propogate_deposit", "comment": "event_recv from branch 3"},
      {"customer-request-id": 2, "logical_clock": 9, "interface": "withdraw", "comment": "event_recv from customer 1"},
      {"customer-request-id": 2, "logical_clock": 10, "interface": "propogate_withdraw", "comment": "event_sent to branch 2"},
      {"customer-request-id": 2, "logical_clock": 11, "interface": "propogate_withdraw", "comment": "event_sent to branch 3"},
      {"customer-request-id": 4, "logical_clock": 14, "interface": "propogate_withdraw", "comment": "event_recv from branch 2"},
      {"customer-request-id": 6, "logical_clock": 15, "interface": "propogate_withdraw", "comment": "event_recv from branch 3"}
    ]
  },
  {
    "id": 2,
    "type": "branch",
    "events": [
      {"customer-request-id": 1, "logical_clock": 4, "interface": "propogate_deposit", "comment": "event_recv from branch 1"},
      {"customer-request-id": 3, "logical_clock": 5, "interface": "deposit", "comment": "event_recv from customer 2"},
      {"customer-request-id": 3, "logical_clock": 6, "interface": "propogate_deposit", "comment": "event_sent to branch 1"},
      {"customer-request-id": 3, "logical_clock": 7, "interface": "propogate_deposit", "comment": "event_sent to branch 3"},
      {"customer-request-id": 2, "logical_clock": 11, "interface": "propogate_withdraw", "comment": "event_recv from branch 1"},
      {"customer-request-id": 4, "logical_clock": 12, "interface": "withdraw", "comment": "event_recv from customer 2"},
      {"customer-request-id": 4, "logical_clock": 13, "interface": "propogate_withdraw", "comment": "event_sent to branch 1"},
      {"customer-request-id": 5, "logical_clock": 14, "interface": "propogate_deposit", "comment": "event_recv from branch 3"},
      {"customer-request-id": 4, "logical_clock": 15, "interface": "propogate_withdraw", "comment": "event_sent to branch 3"},
      {"customer-request-id": 6, "logical_clock": 18, "interface": "propogate_withdraw", "comment": "event_recv from branch 3"}
    ]
  },
  {
    "id": 3,
    "type": "branch",
    "events": [
      {"customer-request-id": 5, "logical_clock": 2, "interface": "deposit", "comment": "event_recv from customer 3"},
      {"customer-request-id": 5, "logical_clock": 3, "interface": "propogate_deposit", "comment": "event_sent to branch 1"},
      {"customer-request-id": 1, "logical_clock": 5, "interface": "propogate_deposit", "comment": "event_recv from branch 1"},
      {"customer-request-id": 5, "logical_clock": 6, "interface": "propogate_deposit", "comment": "event_sent to branch 2"},
      {"customer-request-id": 3, "logical_clock": 8, "interface": "propogate_deposit", "comment": "event_recv from branch 2"},
      {"customer-request-id": 2, "logical_clock": 12, "interface": "propogate_withdraw", "comment": "event_recv from branch 1"},
      {"customer-request-id": 6, "logical_clock": 13, "interface": "withdraw", "comment": "event_recv from customer 3"},
      {"customer-request-id": 6, "logical_clock": 14, "interface": "propogate_withdraw", "comment": "event_sent to branch 1"},
      {"customer-request-id": 4, "logical_clock": 16, "interface": "propogate_withdraw", "comment": "event_recv from branch 2"},
      {"customer-request-id": 6, "logical_clock": 17, "interface": "propogate_withdraw", "comment": "event_sent to branch 2"}
    ]
  }
]
```

### Part 3: Events Triggered by Each Customer Deposit/Withdraw Request

```json
[
  {"id": 1, "customer-request-id": 1, "type": "customer", "logical_clock": 1, "interface": "deposit", "comment": "event_sent from customer 1"},
  {"id": 1, "customer-request-id": 1, "type": "branch", "logical_clock": 2, "interface": "deposit", "comment": "event_recv from customer 1"},
  {"id": 1, "customer-request-id": 1, "type": "branch", "logical_clock": 3, "interface": "propogate_deposit", "comment": "event_sent to branch 2"},
  {"id": 2, "customer-request-id": 1, "type": "branch", "logical_clock": 4, "interface": "propogate_deposit", "comment": "event_recv from branch 1"},
  {"id": 1, "customer-request-id": 1, "type": "branch", "logical_clock": 4, "interface": "propogate_deposit", "comment": "event_sent to branch 3"},
  {"id": 3, "customer-request-id": 1, "type": "branch", "logical_clock": 5, "interface": "propogate_deposit", "comment": "event_recv from branch 1"},

  {"id": 1, "customer-request-id": 2, "type": "customer", "logical_clock": 2, "interface": "withdraw", "comment": "event_sent from customer 1"},
  {"id": 1, "customer-request-id": 2, "type": "branch", "logical_clock": 9, "interface": "withdraw", "comment": "event_recv from customer 1"},
  {"id": 1, "customer-request-id": 2, "type": "branch", "logical_clock": 10, "interface": "propogate_withdraw", "comment": "event_sent to branch 2"},
  {"id": 2, "customer-request-id": 2, "type": "branch", "logical_clock": 11, "interface": "propogate_withdraw", "comment": "event_recv from branch 1"},
  {"id": 1, "customer-request-id": 2, "type": "branch", "logical_clock": 11, "interface": "propogate_withdraw", "comment": "event_sent to branch 3"},
  {"id": 3, "customer-request-id": 2, "type": "branch", "logical_clock": 12, "interface": "propogate_withdraw", "comment": "event_recv from branch 1"},

  {"id": 2, "customer-request-id": 3, "type": "customer", "logical_clock": 1, "interface": "deposit", "comment": "event_sent from customer 2"},
  {"id": 2, "customer-request-id": 3, "type": "branch", "logical_clock": 5, "interface": "deposit", "comment": "event_recv from customer 2"},
  {"id": 2, "customer-request-id": 3, "type": "branch", "logical_clock": 6, "interface": "propogate_deposit", "comment": "event_sent to branch 1"},
  {"id": 2, "customer-request-id": 3, "type": "branch", "logical_clock": 7, "interface": "propogate_deposit", "comment": "event_sent to branch 3"},
  {"id": 1, "customer-request-id": 3, "type": "branch", "logical_clock": 7, "interface": "propogate_deposit", "comment": "event_recv from branch 2"},
  {"id": 3, "customer-request-id": 3, "type": "branch", "logical_clock": 8, "interface": "propogate_deposit", "comment": "event_recv from branch 2"},

  {"id": 2, "customer-request-id": 4, "type": "customer", "logical_clock": 2, "interface": "withdraw", "comment": "event_sent from customer 2"},
  {"id": 2, "customer-request-id": 4, "type": "branch", "logical_clock": 12, "interface": "withdraw", "comment": "event_recv from customer 2"},
  {"id": 2, "customer-request-id": 4, "type": "branch", "logical_clock": 13, "interface": "propogate_withdraw", "comment": "event_sent to branch 1"},
  {"id": 1, "customer-request-id": 4, "type": "branch", "logical_clock": 14, "interface": "propogate_withdraw", "comment": "event_recv from branch 2"},
  {"id": 2, "customer-request-id": 4, "type": "branch", "logical_clock": 15, "interface": "propogate_withdraw", "comment": "event_sent to branch 3"},
  {"id": 3, "customer-request-id": 4, "type": "branch", "logical_clock": 16, "interface": "propogate_withdraw", "comment": "event_recv from branch 2"},

  {"id": 3, "customer-request-id": 5, "type": "customer", "logical_clock": 1, "interface": "deposit", "comment": "event_sent from customer 3"},
  {"id": 3, "customer-request-id": 5, "type": "branch", "logical_clock": 2, "interface": "deposit", "comment": "event_recv from customer 3"},
  {"id": 3, "customer-request-id": 5, "type": "branch", "logical_clock": 3, "interface": "propogate_deposit", "comment": "event_sent to branch 1"},
  {"id": 3, "customer-request-id": 5, "type": "branch", "logical_clock": 6, "interface": "propogate_deposit", "comment": "event_sent to branch 2"},
  {"id": 1, "customer-request-id": 5, "type": "branch", "logical_clock": 8, "interface": "propogate_deposit", "comment": "event_recv from branch 3"},
  {"id": 2, "customer-request-id": 5, "type": "branch", "logical_clock": 14, "interface": "propogate_deposit", "comment": "event_recv from branch 3"},

  {"id": 3, "customer-request-id": 6, "type": "customer", "logical_clock": 2, "interface": "withdraw", "comment": "event_sent from customer 3"},
  {"id": 3, "customer-request-id": 6, "type": "branch", "logical_clock": 13, "interface": "withdraw", "comment": "event_recv from customer 3"},
  {"id": 3, "customer-request-id": 6, "type": "branch", "logical_clock": 14, "interface": "propogate_withdraw", "comment": "event_sent to branch 1"},
  {"id": 1, "customer-request-id": 6, "type": "branch", "logical_clock": 15, "interface": "propogate_withdraw", "comment": "event_recv from branch 3"},
  {"id": 3, "customer-request-id": 6, "type": "branch", "logical_clock": 17, "interface": "propogate_withdraw", "comment": "event_sent to branch 2"},
  {"id": 2, "customer-request-id": 6, "type": "branch", "logical_clock": 18, "interface": "propogate_withdraw", "comment": "event_recv from branch 3"}
]
```

## Formatting Specifications

### File Naming and Execution

- Name the server file `server.py`. All required servers must start with `python server.py input.json`.
- Name the client file `client.py`. It must run with `python client.py input.json`.
- Put the protobuf file in the `protos` directory (for example, `protos/banks.proto`).

### Expected File Structure

```text
.
├── protos
│   └── banks.proto
├── input.json
├── server.py
├── client.py
├── customer.py
├── branch.py
└── output.json
```

## Submission Directions for Deliverables

### Part 1: Written Report

You are given a limited number of attempts to submit your best work. The attempts are intended to address submission errors, such as accidentally submitting the wrong paper; they are not intended to provide multiple rounds of feedback before one final submission. Only the most recent submission will be assessed.

Submit the Logical Clock Project Written Report in its course submission space. Learners may not submit assignments or projects for review, feedback, or grading through email or any other means.

The Written Report deliverable is one PDF named:

`CSE 531_Your Name_Logical Clock_Written Report`

### Part 2: Project Code

You are given unlimited attempts to submit your best work. Submit the Logical Clock Project Code through Gradescope. Review these directions carefully to earn credit. Learners may not submit assignments or projects for review, feedback, or grading through email or any other means.

#### Submitting to Gradescope

1. Go to the Canvas assignment **Submission: Logical Clock Project Code**.
2. Click **Load Submission...in new window**.
3. In Gradescope, select **Submission: Logical Clock Project Code**; a pop-up window will appear.
4. In the pop-up, submit one ZIP file and click **Upload**.
5. The assignment is complete when feedback and a score appear for each test case.
6. To resubmit, click **Resubmit** at the bottom-right of the page and repeat from Step 3.

The Project Code deliverable is one ZIP file containing the project code files and final output. Code files must follow the naming conventions in **Formatting Specifications**. The final output must be a single JSON file named `output.json`.

- Create the ZIP by selecting all files together; code files should be in the root folder of the ZIP.

## Evaluation

Project deliverables are evaluated using the following components. Review the syllabus for late-penalty details.

| Component | Weight | Evaluation method |
| --- | ---: | --- |
| Test Case | 40% | Auto-graded |
| Code | 40% | Course team-graded |
| Report | 20% | Course team-graded |

### Test Case

Each customer and branch has an independent logical clock that is updated during events. The program must handle propagation of `deposit` and `withdraw` events between customers and branches, incrementing and updating the clock whenever an event is sent. It must log event details and write a JSON output that demonstrates correctly propagated, well-ordered events across branches. The logical clock must increase for each event sent from a customer.

The output is checked for correct event ordering. Every event must follow a happens-before relationship; refer to the sample expected output in the project code section. The auto-graded score corresponds to the percentage of returned event values in the correct order: approximately 20%, 40%, 60%, 80%, or 100%.

### Code

The code is graded against the rubric. It must retain the gRPC Project components and add logical clocks for customers and branches plus the logical-clock algorithm:

- `Branch.Query`
- `Branch.Withdraw`
- `Branch.Deposit`
- `Branch.Propogate_Withdraw`
- `Branch.Propagate_Deposit`

Missing project deliverables are graded only against what was submitted. Missing portions submitted after the deadline are not graded.

### Report

The report is graded against the rubric. Missing project deliverables are graded only against what was submitted, and missing portions submitted after the deadline are not graded.

## Rubric Summary

### Test Case

The exemplary criterion is that all events follow a happens-before relationship in the correct order. Lower performance levels correspond to approximately 20%, 40%, 60%, or 80% of events following the correct order.

### Code

To be exemplary, the project code must be functional, perform the functions described in the final report, be excellently engineered, and include helpful documentation and code comments where appropriate.

### Report

The report is assessed in these areas:

- **Problem statement and goal:** The exemplary response is focused and meaningfully connected to the project description.
- **Setup:** The exemplary response is complete, clear, accurate, and has working steps.
- **Implementation processes:** The exemplary response gives a sound explanation with accurate, related, working steps.
- **Results:** The exemplary response presents accurate results and well-developed justifications directly related to implementation results.
