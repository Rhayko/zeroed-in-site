-- 1. Compare channel economics, using ratio-of-sums rather than average margins.
SELECT channel_name,SUM(orders) orders,SUM(net_sales)/100.0 net_sales_usd,
 SUM(contribution_after_marketing)/100.0 contribution_usd,
 ROUND(100.0*SUM(contribution_after_marketing)/NULLIF(SUM(net_sales),0),2) contribution_margin_pct,
 ROUND(100.0*SUM(returned_units)/NULLIF(SUM(units),0),2) unit_return_pct
FROM channel_month_economics GROUP BY channel_id ORDER BY contribution_usd DESC;

-- 2. Product contribution excludes fulfillment and marketing: no invented allocation.
SELECT p.product_name,p.category,SUM(l.quantity) sold_units,SUM(l.returned_units) returned_units,
 SUM(l.net_sales)/100.0 net_sales_usd,SUM(l.product_contribution)/100.0 product_contribution_usd
FROM line_economics l JOIN products p USING(product_id)
GROUP BY p.product_id ORDER BY product_contribution_usd;

-- 3. Window functions compare order-month cohorts after returns mature.
WITH totals AS (SELECT month,SUM(net_sales) net_sales,SUM(contribution_after_marketing) contribution
 FROM channel_month_economics GROUP BY month)
SELECT month,net_sales/100.0 net_sales_usd,contribution/100.0 contribution_usd,
 (net_sales-LAG(net_sales) OVER(ORDER BY month))/100.0 monthly_sales_change_usd
FROM totals ORDER BY month;

-- 4. Negative order contribution: fulfillment charged once, marketing not allocated.
SELECT channel_id,COUNT(*) orders,
 SUM(CASE WHEN contribution_before_marketing<0 THEN 1 ELSE 0 END) negative_contribution_orders
FROM order_economics GROUP BY channel_id;

-- 5. Expose the many-to-many aggregation trap with multiple return events.
SELECT l.line_id,COUNT(r.return_id) return_events,
 l.quantity*l.unit_price_cents correct_gross_cents,
 SUM(l.quantity*l.unit_price_cents) incorrect_direct_join_gross_cents
FROM order_lines l JOIN returns r USING(line_id)
GROUP BY l.line_id HAVING COUNT(r.return_id)>1 ORDER BY l.line_id;
