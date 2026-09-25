# CSE 572: Data Mining - Cluster Validation Project

## Purpose

Apply cluster-validation techniques to data extracted from the provided dataset.

## Objectives

By completing this project, you should be able to:

- Develop code that performs clustering.
- Test and analyze clustering results.
- Assess clustering accuracy using SSE and supervised cluster-validity metrics.

## Technology Requirements

- Python 3.14.5
- scikit-learn 1.9.0
- pandas 2.3.3
- NumPy 2.4.6
- SciPy 1.17.1
- matplotlib 3.11.0

## Project Description

Write a Python program that clusters the supplied training data and validates the clusters to determine the amount of carbohydrates in each meal.

Before beginning, watch the *Cluster Validation Project Introductory* video in Ed Lessons. The overview document is the source of truth if its directions differ from the video.

## Accessing the Assignment

1. In Canvas, open **Submission: Cluster Validation Project**.
2. Select **Load Submission...in new window**.
3. In Ed Lessons, open **Submission: Cluster Validation Project**.
4. Review the code-challenge directions and resources.
5. Complete the work in `main.py`.

## Data

Use the Project 1 data files:

- `CGMData.csv`
- `InsulinData.csv`

The project assumes you have already created the Project 2 Meal Data Matrix, with shape `P x 30`.

## Workflow

### 1. Extract Ground Truth

1. From `InsulinData.csv`, collect all meal-intake values from `BWZ Carb Input (grams)` (column Y) and determine their minimum and maximum.
2. Discretize meal amounts into bins of width 20 grams. The assignment defines the number of bins as `n = (max - min) / 20`.
3. For each row of the `P x 30` Meal Data Matrix, assign it to the bin corresponding to its meal-amount label. These bin assignments are the ground truth.

### 2. Cluster Meal Data

Using the Project 2 features, cluster the meal data into `n` clusters with:

- KMeans
- DBSCAN

### 3. Compute SSE

Compute the within-cluster sum of squared errors (SSE) for every cluster, then combine the values into one total SSE for KMeans and one total SSE for DBSCAN.

### 4. Calculate Entropy and Purity

For each clustering method:

1. Create a matrix whose columns are ground-truth bins (`b1, b2, ..., bn`) and whose rows are clusters (`C1, C2, ..., Cn`).
2. Populate each cell with the number of samples from that cluster that fall in that bin.
3. Calculate entropy and purity using the formulas provided in the introductory video.

## Required Output

Create `Result.csv` as a single row with exactly six values and **no header**:

| Column | Value |
| --- | --- |
| 1 | SSE for KMeans |
| 2 | SSE for DBSCAN |
| 3 | Entropy for KMeans |
| 4 | Entropy for DBSCAN |
| 5 | Purity for KMeans |
| 6 | Purity for DBSCAN |

## Submission

Submit the deliverable through Ed Lessons. Attempts are unlimited, but only the most recent submission is assessed. Do not submit work for grading or feedback through email or other channels.
