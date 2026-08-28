# CSE 572: Data Mining

## Extracting Time Series Properties of Glucose Levels in Artificial Pancreas Project

## Purpose

In this project, you will extract several performance metrics of an Artificial Pancreas system from sensor data.

## Objectives

Learners will be able to:

- Extract feature data from a data set.
- Synchronize data from two sensors.
- Compute and report overall statistical measures from data.

## Technology Requirements

- Python 3.14.5
- scikit-learn 1.9.0
- pandas 2.3.3
- numpy 2.4.6
- scipy 1.17.1

## Project Description

In this project, we are considering the Artificial Pancreas medical control system, specifically the Medtronic 670G system. The Medtronic system consists of a continuous glucose monitor (CGM) and the Guardian Sensor, which is used to collect blood glucose measurements every 5 minutes.

The sensor is single-use and can be used continuously for 7 days, after which it has to be replaced. The replacement procedures include a recalibration process that requires the user to obtain blood glucose measurements using a Contour NextLink 2.4 glucosemeter. This process also requires manual intervention.

The Guardian Link Transmitter powers the CGM sensor and sends the data to the MiniMed 670G insulin pump. The insulin pump utilizes SmartGuard Technology that modulates insulin delivery based on the CGM data. SmartGuard Technology uses a proportional, integrative, and derivative controller to derive small bursts of insulin, also called micro bolus, to be delivered to the user.

During meals, the user uses a Bolus Wizard to compute the amount of food bolus required to maintain blood glucose levels. The user manually estimates carbohydrate intake and enters it into the Bolus Wizard. The Bolus Wizard is pre-configured with the correction factor, body weight, and average insulin sensitivity of the subject, and it calculates the bolus insulin to be delivered. The user can then program the MiniMed 670G infusion pump to deliver that amount.

In addition to the bolus, the MiniMed 670G insulin pump can also provide a correction bolus. The correction bolus amount is provided only if the CGM reading is above a threshold, typically 120 mg/dL, and is a proportional amount with respect to the difference between the CGM reading and the threshold.

SmartGuard Technology has two methods of suspending insulin delivery:

- Suspend on low: insulin delivery is stopped when the CGM reading is less than a certain threshold.
- Suspend on predicted low: insulin delivery is stopped when the CGM reading is predicted to be less than a certain threshold.

Insulin delivery can also be suspended manually by the user or when the insulin reservoir is running low.

## Directions

### Accessing Ed Lessons

Complete and submit your work through Ed Lessons:

1. Go to the Canvas assignment, "Submission: Extracting Time Series Properties of Glucose Levels in Artificial Pancreas Project".
2. Click the "Load Submission...in new window" button.
3. In Ed Lesson, select the assignment titled "Submission: Extracting Time Series Properties of Glucose Levels in Artificial Pancreas Project".
4. In the code challenge, review the directions and resources provided in the description.
5. When ready, start working in the Python file titled `main.py`.

## Project Directions

### Dataset

You will be given two datasets:

- `CGMData.csv`, from the Continuous Glucose Sensor.
- `InsulinData.csv`, from the insulin pump.

The output of the CGM sensor consists of three relevant columns:

- Data timestamp, from columns B and C combined.
- The 5-minute filtered CGM reading in mg/dL, column AE.
- The ISIG value, which is the raw sensor output every 5 minutes.

The output of the pump has the following information:

- Data timestamp.
- Basal setting.
- Micro bolus every 5 minutes.
- Meal intake amount in grams of carbohydrate.
- Meal bolus.
- Correction bolus.
- Correction factor.
- CGM calibration or insulin reservoir-related alarms.
- Auto mode exit events and unique codes representing reasons, column Q.

The bold items in the original document are the columns used in this project.

## Metrics To Be Extracted

Compute the following metrics:

1. Percentage time in hyperglycemia: CGM > 180 mg/dL.
2. Percentage time in hyperglycemia critical: CGM > 250 mg/dL.
3. Percentage time in range: CGM >= 70 mg/dL and CGM <= 180 mg/dL.
4. Percentage time in range secondary: CGM >= 70 mg/dL and CGM <= 150 mg/dL.
5. Percentage time in hypoglycemia level 1: CGM < 70 mg/dL.
6. Percentage time in hypoglycemia level 2: CGM < 54 mg/dL.

Each metric is extracted in three time intervals:

- Daytime: 6:00 AM to midnight.
- Overnight: midnight to 6:00 AM.
- Whole day: 12:00 AM to 12:00 AM.

The percentage is based on the total number of CGM data points that should be available each day. Assume that the total number of CGM data points that should be available is 288. Some days have fewer than 288 available data points, but the percentage should still be calculated with respect to 288.

Extract these metrics for each day and then report the mean value of each metric over all days. There are 18 metrics total.

The metrics are computed for two cases:

- Case A: Manual mode.
- Case B: Auto mode.

## Analysis Procedure

The data is in reverse time order. The first row is the end of data collection, while the last row is the beginning of data collection. The data starts with manual mode.

Manual mode continues until the message `AUTO MODE ACTIVE PLGM OFF` appears in column Q of `InsulinData.csv`. From then onward, auto mode starts. There may be multiple `AUTO MODE ACTIVE PLGM OFF` messages in column Q, but only the earliest one should be used to determine when auto mode starts.

There is no switching back to manual mode, so the first task is to determine the timestamp when auto mode starts.

The timestamp of the CGM data is not the same as the timestamp of the insulin pump data because the two devices operate asynchronously.

Once the start of auto mode is determined from `InsulinData.csv`, find the timestamp in `CGMData.csv` where auto mode starts. This can be done by searching for the timestamp nearest to and later than the auto mode start timestamp obtained from `InsulinData.csv`.

For each user, CGM data is parsed and divided into segments, where each segment corresponds to one day's worth of data. One day starts at 12:00 AM and ends at 11:59 PM. If there is no CGM data loss, there should be 288 samples in each segment.

The whole segment is used to compute the whole-day metrics. Each segment is divided into two sub-segments:

- Daytime sub-segment.
- Overnight sub-segment.

For each sub-segment, count the number of samples that belong to the metric ranges. To compute the percentage with respect to 24 hours, the total number of samples in the specified range is divided by 288.

The data includes a missing data problem. Some days may not have all 288 data points. In the data files, missing data is represented as `NaN`. A strategy is needed to handle missing data, such as deleting the entire day of data or interpolation.

Write a Python script that accepts two CSV files, `CGMData.csv` and `InsulinData.csv`, runs the analysis procedure, and outputs the metrics in another CSV file using the format described in `Result.csv`.

## Submission Directions

The project includes one deliverable:

- `main.py`: use the file provided in the workspace, which also includes all necessary datasets.

Test the work by running:

```bash
python3 main.py
```

Submit the work through Ed Lessons when finished.

## Submitting To Ed Lessons

This project is auto-graded. Complete and submit the work through Ed Lesson's code challenges:

1. Use the `main.py` file provided in the workspace.
2. All necessary datasets are already loaded into the workspace.
3. Execute the code by running `python3 main.py` in the terminal.
4. When ready to submit, click "Test" at the bottom right of the screen.
5. The assignment is complete when feedback appears for each test case with a score.
