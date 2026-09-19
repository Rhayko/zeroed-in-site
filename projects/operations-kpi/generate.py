"""Deterministic, fictional shift-level fulfillment data. Python standard library only."""
import csv, json, random, math, hashlib
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'data'
OUT.mkdir(exist_ok=True)
rng = random.Random(190926)
rows=[]
d=date(2025,7,1)
while d <= date(2025,12,31):
    if d.weekday()<5:
        for site in ['North','South']:
            for shift in ['AM','PM']:
                peak=d.month in [11,12]
                constrained=site=='South' and shift=='PM' and d.month in [9,10]
                due=max(80,round(rng.gauss(230 if site=='North' else 210,28)*(1.18 if peak else 1)*(1.08 if d.weekday()==0 else 1)))
                planned=round((7 if site=='North' else 6)*7.5,1)
                absence=round(rng.uniform(1,6)+(9 if constrained else 0),1)
                regular=round(planned-absence,1)
                ot=round(max(0,rng.gauss(3 if peak or constrained else 1.5,1.3)),1)
                complex_share=min(.55,max(.08,rng.gauss(.32 if site=='South' else .20,.07)))
                complex_orders=round(due*complex_share)
                standard_hours=round(((due-complex_orders)*9+complex_orders*15)/60,2)
                load=standard_hours/regular
                downtime=rng.choice([0,0,0,10,20,35,60])
                carrier=rng.random()<.08
                late_p=min(.36,max(.01,.025+max(load-.85,0)*.25+downtime*.0006+(.065 if carrier else 0)+rng.gauss(0,.007)))
                late=sum(rng.random()<late_p for _ in range(due))
                rework=sum(rng.random()<(.014+complex_share*.04+max(load-1,0)*.015) for _ in range(due))
                weights=[1+max(load-.85,0)*18,1+rework/6,1.5,8 if carrier else .5,1]
                causes=dict.fromkeys(['Capacity','Rework','Stock','Carrier','Other'],0)
                for cause in rng.choices(list(causes),weights=weights,k=late): causes[cause]+=1
                # Rework-attributed late orders must be a subset of reworked orders.
                excess=max(0,causes['Rework']-rework)
                causes['Rework']-=excess
                causes['Other']+=excess
                units=due*2+complex_orders*3+rng.randint(0,due)
                rows.append(dict(record_id=f'{d:%Y%m%d}-{site[0]}-{shift}',date=d.isoformat(),month=d.strftime('%Y-%m'),site=site,shift=shift,orders_due=due,on_time_orders=due-late,late_orders=late,units_shipped=units,rework_orders=rework,planned_hours=planned,regular_hours=regular,overtime_hours=ot,complex_orders=complex_orders,standard_hours=standard_hours,downtime_minutes=downtime,capacity_late=causes['Capacity'],rework_late=causes['Rework'],stock_late=causes['Stock'],carrier_late=causes['Carrier'],other_late=causes['Other']))
    d+=timedelta(days=1)
fields=list(rows[0])
with (OUT/'shift_operations.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
def aggregate(rr):
    totals={k:round(sum(r[k] for r in rr),4) for k in fields[5:]}
    totals.update(records=len(rr),on_time_rate=totals['on_time_orders']/totals['orders_due'],rework_rate=totals['rework_orders']/totals['orders_due'],overtime_share=totals['overtime_hours']/(totals['regular_hours']+totals['overtime_hours']),units_per_hour=totals['units_shipped']/(totals['regular_hours']+totals['overtime_hours']))
    return totals
summary={'overall':aggregate(rows),'months':{},'groups':{},'load_bands':{},'seed':190926}
for month in sorted(set(r['month'] for r in rows)): summary['months'][month]=aggregate([r for r in rows if r['month']==month])
for site in ['North','South']:
    for shift in ['AM','PM']: summary['groups'][f'{site} {shift}']=aggregate([r for r in rows if r['site']==site and r['shift']==shift])
for label,selector in [('At or below capacity',lambda r:r['standard_hours']<=r['regular_hours']),('Above capacity',lambda r:r['standard_hours']>r['regular_hours'])]: summary['load_bands'][label]=aggregate([r for r in rows if selector(r)])
summary['delay_reasons']=sorted([{'reason':name,'orders':summary['overall'][col]} for name,col in [('Capacity','capacity_late'),('Rework','rework_late'),('Stock','stock_late'),('Carrier','carrier_late'),('Other','other_late')]],key=lambda x:-x['orders'])
checks={
 'unique_record_keys':len({r['record_id'] for r in rows})==len(rows),
 'complete_date_site_shift_grid':len(rows)==len({r['date'] for r in rows})*4,
 'no_missing_fields':all(all(v is not None and v!='' for v in r.values()) for r in rows),
 'on_time_plus_late_equals_due':all(r['on_time_orders']+r['late_orders']==r['orders_due'] for r in rows),
 'mutually_exclusive_delay_reasons_reconcile':all(sum(r[c] for c in ['capacity_late','rework_late','stock_late','carrier_late','other_late'])==r['late_orders'] for r in rows),
 'positive_hours':all(r['regular_hours']>0 and r['overtime_hours']>=0 for r in rows),
 'subset_bounds':all(0<=r['rework_late']<=r['rework_orders']<=r['orders_due'] and 0<=r['complex_orders']<=r['orders_due'] for r in rows),
 'nonnegative_measures':all(r[c]>=0 for r in rows for c in fields[5:]),
 'monthly_order_totals_reconcile':sum(m['orders_due'] for m in summary['months'].values())==summary['overall']['orders_due'],
 'group_order_totals_reconcile':sum(m['orders_due'] for m in summary['groups'].values())==summary['overall']['orders_due']}
assert all(checks.values()),checks
summary['checks']=checks
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
(OUT/'rows.json').write_text(json.dumps(rows))
(OUT/'validation.json').write_text(json.dumps({'checks':checks,'csv_sha256':hashlib.sha256((OUT/'shift_operations.csv').read_bytes()).hexdigest()},indent=2))
print(json.dumps(summary,indent=2))
