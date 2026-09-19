# Demand Forecasting & Model Evaluation

Independent Portfolio Project | Synthetic Dataset

## Decision
Which transparent baseline should a planner use for a twelve-week product demand outlook? Compare models on earlier chronological windows, lock the choice for each product, then evaluate forecasts against a separate final period. This project demonstrates evaluation discipline rather than a claim that a complex model is necessary.

## Data and design
The generator creates 1,056 product-week records: eight products over 132 consecutive Mondays beginning January 2, 2023. Demand is integer, nonnegative and includes seasonal variation, trend, independent noise and intermittent zero demand for utility totes. These patterns are explicit simulation assumptions, not observed market behavior. The generator seed is 4192026. These product series are independently generated and are not joined to the commerce dataset in Project 3, despite shared fictional product names.

Columns: `week_start` is the Monday date; `week_index` is a zero-based sequence from 0 to 131; `product` identifies a series; `demand_units` is uncensored weekly demand. This is demand, not sales constrained by available inventory. Promotions, prices, lead-time variability and stockouts are excluded.

## Evaluation protocol
Three expanding-window validation origins are week 84, 96 and 108. At each origin, models receive only preceding observations and predict the next twelve weeks. For each product, select the model with the lowest mean absolute error across the 36 validation weeks. Fixed model order breaks exact ties. These windows determine model selection, not final reported test performance.

Refit the selected model using weeks 0–119, then issue twelve forecasts for weeks 120–131 at once. Do not update forecasts within the holdout. Final observations are used only to score predictions. A test changes every holdout observation and confirms that model selection and forecasts remain unchanged.

Models:
- Seasonal naive: use the observation from 52 weeks before each target week.
- Recent mean: repeat the mean of the latest 13 training weeks.
- Scaled seasonal: multiply seasonal-naive predictions by the ratio of the latest 13 training weeks to the corresponding 13 weeks a year earlier. If the earlier total is zero, use scale 1. No holdout values enter the ratio.

Models are intentionally simple, interpretable baselines. Predictions retain fractional units for unbiased evaluation; no order-quantity rounding or inventory decision is implied.

## Metrics and interpretation
MAE is mean absolute error in units per product-week. RMSE penalizes large errors more heavily. WAPE is total absolute error divided by total actual demand across the selected population; it is not the average of individual percentage errors. It is undefined when the actual total is zero. Bias is mean forecast minus actual; positive means overforecasting.

The portfolio comparison uses all 96 product-week holdout observations. Weekly chart lines sum the eight series, which can conceal offsetting errors; the product error chart and downloadable records expose that limitation. A single twelve-week holdout is small and serially dependent. No confidence interval, statistical significance, inventory savings or service-level guarantee is claimed. Choosing the winner from holdout results would invalidate the test.

## Reproduce
Python 3.10+; dependency versions are pinned in requirements.txt.

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 analyze.py --output results/my-run
python3 -m unittest discover -s . -p test_analysis.py -v
```

On Windows activate with `.venv\Scripts\activate`. Choose a new directory for each run. `results/reference` contains the supplied results. `report.json` holds full-precision metrics and selected models; CSVs contain generated data, validation scores, model selections and all three models' holdout predictions. `holdout-analysis.png` is a standalone Matplotlib chart.

## Checks and next decision
Thirteen automated tests cover repeatability, complete unique keys, nonnegative demand, hand-calculated forecasts and error metrics, zero demand, invalid input, prediction grain, minimum validation error selection and holdout leakage resistance.

Use the selected models as a benchmark for a future forecasting pilot. Examine poor-performing products before operational adoption. Real deployment requires additional rolling test periods, inventory availability, promotional covariates and asymmetric shortage/overstock costs. This script is an analytical demonstration, not an automated procurement system.
