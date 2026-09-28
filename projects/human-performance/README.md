# Human Performance Research Analysis

Independent Portfolio Project | Synthetic Dataset

## Research question
In a simulated repeated-measures study, how do a rested and a sleep-restricted condition differ in reaction time, and how strongly is sleep duration associated with reaction time across sessions?

The dataset contains 96 fictional participants measured once in each condition. It demonstrates tidy repeated-measures data, descriptive statistics, a paired t-test, a confidence interval, Pearson correlation, simple linear regression and a Matplotlib research figure.

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

## Study design and data contract
One row is one participant-condition session. Every participant has one Rested and one Restricted record. `condition_order` alternates across participant IDs to represent a balanced order field, although the simulation does not include a carryover effect. Reaction time is milliseconds, where lower is faster. Countermovement jump is centimeters.

The generator explicitly makes longer sleep associated with faster reaction time and slightly greater jump height. These are simulation assumptions. They are not observed physiological findings and should not be presented as evidence for a real population.

## Statistical workflow
1. Validate required fields and confirm one record per participant-condition pair.
2. Summarize sample size, mean and standard deviation by condition.
3. Pivot to participant pairs and test Restricted minus Rested reaction time with a two-sided paired t-test.
4. Calculate a 95% t interval for the mean paired difference.
5. Calculate Pearson correlation between sleep hours and reaction time. Report approximate two-sided p-values with documented large-sample normal/Fisher transformations.
6. Fit a one-predictor ordinary least-squares line with NumPy and report its slope and R-squared.
7. Export source data, summaries, full-precision JSON and a clearly labeled scatterplot.

## Interpretation and limitations
The paired test is appropriate because the same fictional participants appear in both conditions. An independent-groups test would discard that pairing. The regression describes a linear association and does not control for repeated observations, participant characteristics, learning, order or carryover. A production research analysis would use a preregistered protocol, verified instrumentation, missing-data rules, assumption checks and a mixed-effects model when repeated observations require participant-level random effects.

The simulated sample is convenient, complete and balanced. No clinical, training or safety recommendation should be based on it.

## Files
- `analyze.py`: generator, validation, statistics and figure.
- `test_analysis.py`: reproducibility, pairing and reconciliation tests.
- `results/reference/performance_sessions.csv`: synthetic session-level data.
- `results/reference/condition_summary.csv`: descriptive statistics.
- `results/reference/report.json`: hypothesis test, confidence interval, correlation and regression.
- `results/reference/sleep-reaction-analysis.png`: research figure.
