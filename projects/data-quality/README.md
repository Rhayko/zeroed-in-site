# Data Quality & Cleaning System

Independent Portfolio Project | Synthetic Dataset

## Decision and scope
A dispatch dashboard is only trustworthy when each shift has one valid record. This project builds a repeatable intake gate for the synthetic ledger used in the Operations KPI Dashboard. It standardizes declared formatting differences, validates accounting relationships and separates records that require investigation. It does not infer a missing business fact.

The fixture covers 528 weekday/site/shift keys across July–December 2025, with North/South sites and AM/PM shifts. It deliberately contains 554 submitted rows: format variations, missing values, impossible dates, invalid numbers, duplicate submissions and conflicting versions. These defects were injected for testing; they are not evidence of a real business improvement.

## Reproduce
Python 3.10 or later is required. From the extracted project directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 pipeline.py --input data/raw_shift_feed.csv --output results/my-run
```

On Windows, activate with `.venv\Scripts\activate` instead. Choose a new output directory for each run: existing results are never overwritten. `python3 generate_fixture.py` reproduces the supplied corrupted input and independent expected-key list. The production pipeline never reads baseline.csv or expected.json.

## Validated result
37 automated tests pass. All 554 input rows reconcile to 498 accepted, 36 quarantined, 12 exact duplicates and 8 duplicates equivalent after normalization. Quarantine contains 24 invalid rows and 12 conflicting versions of six keys. In total 30 underlying keys need review. There are 68 field-normalization events across 48 submitted rows; this includes duplicate records, not just accepted rows.

The 498 accepted records exactly match their corresponding baseline values in the fixture oracle. Shuffle tests confirm stable accepted results and counts. Reprocessing accepted output produces no further changes.

Accepted records represent 118,000 orders, of which 109,051 are on time (92.42%). This is a metric for the accepted subset ONLY. Exclusions change the population, so it is not a before/after performance improvement. No missing records are reconstructed. Data quality checks cannot establish that a plausible source value is factually true.

## Contract and decision policy
- Header names and order must match data/baseline.csv; all 21 fields are required. Malformed schema, row width and empty feeds fail without publishing a result directory.
- Strip surrounding whitespace; canonicalize North/South and AM/PM by case only. Unknown categories are held, never guessed.
- Dates accept ISO YYYY-MM-DD or explicitly US MM/DD/YYYY. No locale inference. Counts accept nonnegative integers, including integral decimal forms and properly grouped thousands separators. Hours are nonnegative decimals. Missing values stay missing; zero is preserved when allowed.
- Orders due and regular hours must be positive. On-time plus late orders must equal orders due. The five late-reason counts must total late orders. Complex/rework orders cannot exceed orders due; rework-related late orders cannot exceed rework orders. Regular hours cannot exceed planned hours. Date, month and key dimensions must agree.
- Remove exact repeat submissions and valid records identical after normalization. A duplicate designation references a representative row; it does not guarantee that representative passed validation.
- When surviving versions share a valid record ID but disagree, quarantine every version. An invalid conflicting version also blocks a valid version. There is no arbitrary “latest wins” policy without trustworthy source timestamps.
- Do not cap statistical outliers or fill missing values. Review exceptions with the source owner, obtain a corrected feed and process it into a new run directory. Retain prior evidence.

## Output evidence
`clean.csv`: accepted canonical records, sorted by key.
`quarantine.csv`: original fields plus source line and reason codes.
`row_disposition.csv`: one final disposition for every submitted row, duplicate lineage and raw-row hash.
`transformations.csv`: every applied formatting change, before/after and final row disposition.
`violations.csv`: field-level failures; more than one may apply to a row.
`raw_evidence.json`: exact parsed input strings in input order; source line is array index + 2 for this single-line-record feed.
`report.json`: counts, accepted-subset metrics and input SHA-256.

CSV audit exports prefix potentially executable nonnumeric text with an apostrophe for spreadsheet safety. Exact unmodified strings remain in raw_evidence.json and the input CSV. Import CSV columns explicitly when spreadsheet auto-detection would change text values. No Excel workbook or native PivotTable is part of this project.

## Design limits
This is an in-memory, single-file batch pipeline, not a production ingestion service. The contract is specific to this dispatch ledger. It does not authenticate sources, infer missing shifts, enforce expected calendar coverage, resolve source disputes or measure live drift. Source-line identifiers refer to CSV record positions (including the header), not physical lines for multiline quoted fields. The synthetic baseline assumes all due orders dispatch the same day and includes weekdays that may be holidays. Normalization and test coverage do not guarantee every possible input is error-free.

The baseline is supplied for transparent fixture verification; the shipped pipeline remains independent of it. Next production steps would be versioned source contracts, source-system identifiers, approved exception ownership and monitoring for schema/distribution changes.
