# Power BI Desktop handoff — not yet native-tested

The SQL/browser deliverables are complete. This package does not contain a .pbix report. These instructions and measures are a starting point for building and validating one in Power BI Desktop; do not describe them as a completed Power BI dashboard.

1. Import `results/reference/channel_month_economics.csv` with Text/CSV. Name the table `ChannelMonth`. It has 24 rows, one per channel-month. Keep month and channel identifiers as text; set financial and count columns to Whole Number.
2. Use the measures in `measures.dax`. Stored monetary amounts are cents, so measures divide by 100. Format monetary measures as USD, rates as percentages and count measures as whole numbers.
3. Add month and channel_name slicers; cards for net sales, contribution, margin and unit return rate; a channel comparison bar chart; a monthly trend; and a cost bridge table. Sort the YYYY-MM month labels ascending.
4. For product diagnostics import `line_economics.csv` and `products.csv` separately. Relate products[product_id] one-to-many to line_economics[product_id] with single-direction filtering. Do not connect line data to ChannelMonth and sum repeated marketing costs. Use a separate product page clearly labeled contribution before fulfillment and marketing.
5. Native validation: full portfolio net sales must be $218,018.90 and contribution $22,414.06. Paid-social net sales must be $56,133.30 and contribution −$14,952.42. Confirm totals are ratios of sums, month/channel filters agree with the SQL exports, and clear/reset restores the full totals. Check a zero-sales fixture returns a blank margin. Refresh, save, close and reopen without errors before release.

The browser preview is an independent HTML/JavaScript dashboard reading SQL-produced results. It is not an embedded Power BI report.
