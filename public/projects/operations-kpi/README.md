# Operations KPI Dashboard

Independent Portfolio Project | Synthetic Dataset

## Decision
Where should a fictional fulfillment operation focus a dispatch-reliability pilot?
The operation has two sites and two daily shifts. Managers need to balance service,
quality and productive labor without treating increased throughput as proof of improvement.

## Evidence
- **124,665 orders represented in 528 shift records**, July–December 2025. These are aggregated records, not 124,665 individual order rows.
- **92.5% on-time dispatch**, versus an illustrative 95% target. 9,298 orders missed dispatch cutoff. This is not a customer delivery metric.
- **South PM: 89.7% on time**, with 3,072 late orders. This group represents 23.9% of volume but 33.0% of late orders.
- **Capacity: 3,856 late orders (41.5%)**, the largest recorded primary reason. Reasons are simulated classifications, not verified root causes.
- **Peak-period tradeoff:** units per direct labor hour rose from 15.4 in July to 18.0 in December, while on-time dispatch fell from 94.0% to 91.0%. Volume and product mix differ across periods.
- **Workload association:** shifts above modeled regular capacity had 88.3% on-time dispatch, versus 95.1% at or below capacity. This is descriptive and confounded by site, shift, demand and product mix.

## Recommendation to test, not a claimed result
Start a limited South PM pilot with earlier identification of overloaded work packets,
cross-trained coverage before cutoff and a check of stock availability before release.
First validate standard-time assumptions and recorded delay reasons with a sample of actual process observations.

For a real pilot, capture four weeks of baseline and four weeks of trial data at order level.
Keep promised cutoff definitions fixed. Compare the same weekdays and stratify simple/complex orders.
Use South AM as contextual comparison, not a randomized control. Track on-time dispatch as the primary outcome,
with rework and overtime as guardrails. Review daily exceptions and report numerator/denominator counts.
A reasonable provisional success rule is at least +2 percentage points in on-time dispatch without more than
0.5 percentage points of additional rework or 2 percentage points of additional overtime share.
These are proposed decision rules, not measured gains or a statistical power calculation.
Do not extrapolate savings without actual wage, cost and intervention data.

## Workbook
- **Dashboard:** editable Site and Shift selectors; editable illustrative targets; formula-driven KPI table, monthly line chart and delay-reason chart. All filter-sensitive results use the same population.
- **Shift data:** 528 typed records in the `ShiftOperations` Excel table.
- **Pivot review:** native Excel PivotTable of site/shift totals, with a populated cache. This view uses all dates and is independent of Dashboard selectors. Use Excel Refresh All after source edits.
- **Definitions:** metrics, cohort boundary, generator assumptions and limits.

The dataset has fixed coverage. To add dates, extend dashboard formula ranges and the PivotTable source range.
Do not paste beyond the source range and assume it is included. SUMIFS formulas use bounded ranges.
Rates are ratios of sums. Averaging daily percentages would give low-volume shifts excess weight.
The PivotTable sums additive measures. Compute rates outside it using matching summed measures.

## Cohort and model assumptions
Every simulated daily shift cohort is completely dispatched that day. Late orders finish after the promised
dispatch cutoff but within that day. Open backlog, cancellations, returns and cross-day carryover are outside scope.
All weekdays operate, including holidays.
`regular_hours` and `overtime_hours` measure direct productive labor, not paid attendance or a measure of employee effort.

Seed 190926 creates higher demand in November and December, reduced South PM regular hours in September and October,
more complex work at South, variable equipment downtime and occasional carrier events. Standard hours assume
9 minutes for simple orders and 15 for complex orders. The generator explicitly uses workload to influence late probability.
It also uses weighted random categories to assign one primary reason to each late order. Rework and lateness may overlap,
but a reworked order is not necessarily late and a late order is assigned only one primary reason.

**These are designed simulation patterns. Finding them demonstrates calculation and interpretation skills,
not independent empirical validation.** Aggregate data cannot establish order-level causal effects or uncertainty.
No hypothesis-test p-values, causal improvements, actual employer results or savings are claimed.

## Reproduce the analysis
Requires Python 3.10+; standard library only.

```sh
python3 generate.py
python3 verify.py
```

`generate.py` reproduces `data/shift_operations.csv`, `data/summary.json`, and `data/validation.json` from the fixed seed.
`verify.py` independently reloads the CSV, recomputes headline metrics and checks negative test cases.
The workbook is supplied separately and is not rebuilt by these two commands.
The browser case-study filters aggregate the same 528 records.

## Validation and remaining limitation
Ten generation checks cover keys, complete coverage, missing fields, population reconciliation, reason reconciliation,
positive hours, subset bounds, nonnegative values and group/month totals. Independent CSV validation includes intentionally
corrupted duplicates, mismatched late totals and zero hours. Workbook formula checks cover the all-record result,
South PM selection, an unmatched selector and a source-cell change. A formula-error scan found no errors.
All four workbook tabs were rendered and inspected. Version 1.0 produced an Excel recovery warning for the PivotTable definition.
Version 1.1 uses the Excel-repaired and Excel-saved workbook. All original source values and formulas were compared cell by cell.
The corrected file retains both charts, both selectors and the native PivotTable with its 528-record cache. Its cached KPIs
match independent totals. A regression check now rejects the inconsistent subtotal definition found in version 1.0.
The reviewer confirmed that the version 1.1 workbook opens and Refresh All runs without errors.
Use the version 1.1 file, not the earlier downloaded workbook. See release-checks.json for the exact file hash and test status.

## Interview discussion
1. Explain why 528 source rows represent 124,665 orders and why the distinction matters.
2. Demonstrate the South/PM filters and trace on-time dispatch to its numerator and denominator.
3. Explain why higher units/hour can coexist with poorer service and why product mix matters.
4. Distinguish recorded delay reason, workload association, and causal evidence.
5. Explain what order-level fields and comparison design you would require before recommending a permanent change.
