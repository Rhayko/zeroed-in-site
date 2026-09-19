# Business Operations Analysis: revenue versus contribution

Independent Portfolio Project | Synthetic Dataset

## Business decision
Which channel should receive a closer margin review before the next promotional budget is set? Revenue alone ignores discounts, returns, product costs, fulfillment and marketing. This case uses six related tables to reconcile those components without multiplying sales or costs through joins.

The completed deliverables are a SQLite database, executable SQL model and analyses, reproducible synthetic generator, 16 automated tests, CSV exports and a browser dashboard. Power BI measures and setup instructions are supplied as a handoff; a native Power BI report has NOT been built or validated.

## Dataset and timing
Seed 3192026 generates 2,400 completed orders, 4,021 order lines and 852 unit-level return events for nine fictional products across four channels. Order dates span July–December 2025. Snapshot: February 1, 2026. All simulated returns occur within 30 days, so the final order cohort has a complete return window. Figures are assigned to the ORIGINAL ORDER MONTH, not the accounting month in which a refund was issued.

All money is USD stored as integer cents. This is a deliberately designed simulation: paid-social orders receive deeper discounts and higher return probabilities. That relationship is an input assumption, not a discovered causal effect or an estimate of real channel performance. Other channels also have returns and promotions.

## Reproduce
Python 3.10+; standard library only. From the extracted folder:

```sh
python3 build.py --output results/my-run
python3 -m unittest discover -s . -p test_model.py -v
```

Choose a new directory for each run. The supplied reference database is in `results/reference/commerce.sqlite`. Open it in a SQLite-compatible SQL editor and run `analysis.sql`. The five queries cover channel economics, product contribution, monthly trends with LAG, negative-contribution orders and a demonstration of join inflation. `model.sql` contains schema, constraints, indexes and analytical views.

## Data dictionary and grain
| Table | Grain and key | Measures / relationships |
|---|---|---|
| channels | One row per channel_id | Display name |
| products | One row per product_id | Name and category; transaction prices/costs live on lines |
| orders | One row per order_id | Order date; channel FK; once-per-order fulfillment cost |
| order_lines | One row per line_id | Order and product FKs; quantity, historical unit price/cost, total line discount |
| returns | One row per return_id | Line FK; return date, returned quantity, refund, recovered product cost, return-processing cost |
| channel_spend | One row per month + channel_id | Actual modeled marketing cost; zero for Direct |

`line_economics` aggregates returns before joining to lines. `order_economics` aggregates lines before subtracting fulfillment once. `channel_month_economics` joins aggregated orders to spend using a union of their keys, retaining spend-only months. These are different grains: do not join them together and sum repeated totals.

## Metric contract
- Gross sales = quantity × transaction unit price, before discounts and refunds.
- Net sales = gross sales − discounts − refunds. Shipping revenue, sales tax, cancellations and chargebacks are outside scope.
- Net product cost = sold quantity × transaction unit cost − recovered cost of restockable returns. A nonrestockable return retains its original product cost.
- Product contribution = net sales − net product cost − return-processing costs. It excludes fulfillment and marketing; no arbitrary product allocation is presented.
- Contribution before marketing = product contribution − once-per-order fulfillment cost.
- Contribution after marketing = contribution before marketing − channel-month marketing spend.
- Contribution margin = SUM(contribution after marketing) / SUM(net sales). A zero sales denominator produces no percentage, not zero percent.
- Unit return rate = SUM(returned units) / SUM(sold units). It is not the fraction of orders with returns.

Contribution is NOT operating profit: fixed overhead, salaries, payment fees, taxes and financing are excluded. Orders count completed orders including fully returned orders. All refunds equal the discounted unit selling price. Original outbound fulfillment is not recovered upon return. Return processing is $3.50 per unit; restockable returned units recover original unit cost.

## Reference findings and recommendation
Net sales total $218,018.90; contribution after marketing is $22,414.06. Paid social records $56,133.30 net sales but −$14,952.42 contribution. Its 26.28% unit-return rate compares with roughly 10% in the other channels. Direct generates $21,637.02 contribution, but has no allocated marketing cost in this model—this does not establish that direct traffic is free to acquire.

Recommend reviewing paid-social discount depth, return reasons, creative/product fit and acquisition costs before increasing its budget. Do not claim reallocating spend will reproduce another channel’s average margin: selection, attribution and incremental demand are unobserved. A real decision would need reconciled invoices, return reason codes, incremental acquisition evidence and a controlled budget test.

## Verification and limits
16 automated tests cover referential and database integrity, stable grains, fulfillment/spend conservation, return bounds and timing, independent whole-dataset and channel-month reconciliation, executable SQL, reproducibility, no-overwrite behavior, spend-only months and hand-calculated partial/full-return scenarios. A line can have multiple return events; the deliberately incorrect direct-join query demonstrates why preaggregation matters.

This generator creates a valid demonstration database; it is not a general-purpose ingestion or data-cleaning service. Some cross-row business constraints are verified in tests rather than enforced by database triggers. SQLite syntax may need adjustment in another SQL engine. No causal attribution, customer lifetime value or production forecasting is attempted. See POWER-BI.md for the optional, unvalidated desktop handoff.
