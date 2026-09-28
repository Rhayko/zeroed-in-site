# Workforce Planning Analysis

Independent Portfolio Project | Synthetic Dataset

## Business question
Where should an HR business partner ask better questions about voluntary turnover, overtime and engagement before planning retention work?

This case creates 720 fictional employee records for 2025. It summarizes department-level turnover and workload, retains missing engagement values, calculates a 95% Wilson confidence interval for the overall turnover rate and compares overtime between employees who exited and employees who stayed with a Welch t-test.

## Reproduce
Python 3.10 or later is required.

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 analyze.py --output results/my-run
python3 -m unittest -v test_analysis.py
```

Use a new output directory for each run. The script refuses to overwrite an existing directory.

## Data contract
One row represents one fictional employee observed during 2025. `employee_id` is unique. `voluntary_exit_2025` is 1 for a modeled voluntary exit and 0 otherwise. Overtime covers Q4; absence, training and exit fields cover 2025. Engagement is a 0–100 simulated survey score. Twenty-nine engagement scores are deliberately missing and remain missing rather than being filled with a department average.

The simulation encodes relationships among overtime, engagement, tenure and exit probability. Those relationships are design choices. They are not evidence about real workers and do not support individual employment decisions. The reported two-sided p-value uses a documented large-sample normal approximation to the Welch statistic.

## Analytical workflow
1. Generate a reproducible sample with a fixed random seed.
2. Validate required columns, employee-key uniqueness and the exit indicator.
3. Aggregate employees and exits before calculating department turnover rates.
4. Report missing engagement counts and use available scores only for department means.
5. Calculate a Wilson interval for the overall exit proportion.
6. Use a two-sided Welch t-test to compare mean Q4 overtime for exits and non-exits.
7. Export the row-level sample, department summary, full-precision JSON results and chart.

## Interpretation and limitations
The department comparison is a prompt for investigation, not a performance ranking. A small p-value only indicates that the synthetic groups differ under the assumptions of the test. It does not show that overtime caused exits. Job type, scheduling, compensation, manager practices and local labor markets are not measured. The records are cross-sectional, the simulation is intentionally simplified and no predictive model is used for employee-level decisions.

In a real analysis, confirm definitions with HR, restrict access to appropriate staff, review fairness and privacy, reconcile employee status to the HR system, compare matched time windows and pair quantitative results with exit themes and manager interviews.

## Files
- `analyze.py`: generator, validation, summary statistics and chart.
- `test_analysis.py`: reproducibility, reconciliation and boundary tests.
- `results/reference/workforce_records.csv`: synthetic row-level data.
- `results/reference/department_summary.csv`: department metrics.
- `results/reference/report.json`: full-precision statistical results.
- `results/reference/turnover-by-department.png`: portfolio chart.
