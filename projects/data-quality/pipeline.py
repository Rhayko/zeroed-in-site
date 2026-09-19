"""Conservative shift-feed validation with explicit lineage. Python 3.10+, pandas 2.x/3.x."""
from __future__ import annotations
import argparse,csv,hashlib,json,re,sys,tempfile,os
from collections import Counter,defaultdict
from datetime import datetime
from decimal import Decimal,InvalidOperation
from pathlib import Path
import pandas as pd

VERSION='1.0.0'
FIELDS=['record_id','date','month','site','shift','orders_due','on_time_orders','late_orders','units_shipped','rework_orders','planned_hours','regular_hours','overtime_hours','complex_orders','standard_hours','downtime_minutes','capacity_late','rework_late','stock_late','carrier_late','other_late']
NUMERIC=FIELDS[5:]
HOURS={'planned_hours','regular_hours','overtime_hours','standard_hours'}
COUNTS=set(NUMERIC)-HOURS
REASONS=['capacity_late','rework_late','stock_late','carrier_late','other_late']
NUMBER=re.compile(r'^[+-]?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$')
def text(value):
    if isinstance(value,Decimal):return format(value,'f')
    return str(value) if value is not None else ''
def serial(values):return json.dumps(values,sort_keys=True,default=text,separators=(',',':'))
def hashrow(r):return hashlib.sha256(serial(r).encode()).hexdigest()
def normalize(raw):
    clean={};issues=[];fixes=[]
    for field in FIELDS:
        value=raw[field];v=value.strip()
        if not v:
            clean[field]=None;issues.append((field,'MISSING_VALUE'));continue
        result=v
        if field in NUMERIC:
            if not NUMBER.fullmatch(v):issues.append((field,'INVALID_NUMBER'));result=None
            else:
                result=Decimal(v.replace(',',''))
                if field in COUNTS:
                    if result!=result.to_integral_value():issues.append((field,'NONINTEGER_COUNT'));result=None
                    else:result=int(result)
        elif field=='site':
            result={'north':'North','south':'South'}.get(v.lower())
            if result is None:issues.append((field,'UNKNOWN_CATEGORY'))
        elif field=='shift':
            result={'am':'AM','pm':'PM'}.get(v.lower())
            if result is None:issues.append((field,'UNKNOWN_CATEGORY'))
        elif field=='date':
            result=None
            for pattern,fmt in [(r'\d{4}-\d{2}-\d{2}','%Y-%m-%d'),(r'\d{2}/\d{2}/\d{4}','%m/%d/%Y')]:
                if re.fullmatch(pattern,v):
                    try:result=datetime.strptime(v,fmt).date().isoformat()
                    except ValueError:pass
                    break
            if result is None:issues.append((field,'INVALID_DATE'))
        elif field=='month' and not re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])',v):
            result=None;issues.append((field,'INVALID_MONTH'))
        elif field=='record_id' and not re.fullmatch(r'\d{8}-[NS]-(?:AM|PM)',v):
            result=None;issues.append((field,'INVALID_KEY'))
        clean[field]=result
        if result is not None and text(result)!=value:fixes.append((field,value,text(result)))
    for field in NUMERIC:
        if clean[field] is not None and clean[field]<0:issues.append((field,'NEGATIVE_VALUE'))
    if clean['regular_hours'] is not None and clean['regular_hours']<=0:issues.append(('regular_hours','NONPOSITIVE_HOURS'))
    def present(*fields):return all(clean[k] is not None for k in fields)
    if present('orders_due') and clean['orders_due']<=0:issues.append(('orders_due','NONPOSITIVE_ORDERS'))
    if present('orders_due','on_time_orders','late_orders') and clean['on_time_orders']+clean['late_orders']!=clean['orders_due']:issues.append(('on_time_orders','ORDER_RECONCILIATION'))
    if present('late_orders',*REASONS) and sum(clean[k] for k in REASONS)!=clean['late_orders']:issues.append(('late_orders','REASON_RECONCILIATION'))
    for child,parent in [('complex_orders','orders_due'),('rework_orders','orders_due'),('rework_late','rework_orders')]:
        if present(child,parent) and clean[child]>clean[parent]:issues.append((child,'SUBSET_BOUNDS'))
    if present('date','month') and clean['date'][:7]!=clean['month']:issues.append(('month','MONTH_MISMATCH'))
    if present('record_id','date','site','shift'):
        expected=clean['date'].replace('-','')+'-'+clean['site'][0]+'-'+clean['shift']
        if clean['record_id']!=expected:issues.append(('record_id','KEY_DIMENSION_MISMATCH'))
    if present('regular_hours','planned_hours') and clean['regular_hours']>clean['planned_hours']:issues.append(('regular_hours','HOURS_BOUNDS'))
    return clean,sorted(set(issues)),fixes

def process(raw_rows):
    records=[];audit=[];raw_seen={};norm_seen={}
    # Stable representative selection: raw-value hash, then source position for identical rows.
    for pos,raw in enumerate(raw_rows,2):
        clean,errors,fixes=normalize(raw)
        records.append(dict(line=pos,raw=raw,clean=clean,errors=errors,fixes=fixes,raw_hash=hashrow(raw),status=None,parent=None))
    ordered=sorted(records,key=lambda r:(r['raw_hash'],r['line']))
    for rec in ordered:
        sig=serial(rec['raw'])
        if sig in raw_seen:rec['status']='DUPLICATE_EXACT';rec['parent']=raw_seen[sig];continue
        raw_seen[sig]=rec['line']
        # Only fully valid rows may be deduplicated by canonical values.
        if not rec['errors']:
            sig=serial(rec['clean'])
            if sig in norm_seen:rec['status']='DUPLICATE_NORMALIZED';rec['parent']=norm_seen[sig];continue
            norm_seen[sig]=rec['line']
    groups=defaultdict(list)
    for rec in records:
        if rec['status'] is None and rec['clean']['record_id']:groups[rec['clean']['record_id']].append(rec)
    for key,group in groups.items():
        if len(group)>1:
            for rec in group:rec['errors'].append(('record_id','DUPLICATE_CONFLICT'))
    accepted=[];quarantine=[];dispositions=[];events=[]
    for rec in sorted(records,key=lambda r:r['line']):
        rec['status']=rec['status'] or ('QUARANTINED' if rec['errors'] else 'ACCEPTED')
        for field,before,after in rec['fixes']:events.append(dict(source_line=rec['line'],record_id=rec['clean']['record_id'] or rec['raw']['record_id'],field=field,before=before,after=after,final_disposition=rec['status']))
        codes=sorted(set(code for _,code in rec['errors']))
        dispositions.append(dict(source_line=rec['line'],record_id=rec['clean']['record_id'] or rec['raw']['record_id'],disposition=rec['status'],reason_codes=';'.join(codes),duplicate_of_line=rec['parent'] or '',raw_row_sha256=rec['raw_hash']))
        if rec['status']=='ACCEPTED':accepted.append(rec['clean'])
        if rec['status']=='QUARANTINED':quarantine.append(dict(source_line=rec['line'],reason_codes=';'.join(codes),**rec['raw']))
        for field,code in rec['errors']:audit.append(dict(source_line=rec['line'],record_id=rec['clean']['record_id'] or rec['raw']['record_id'],field=field,rule=code,value=rec['raw'].get(field,'')))
    accepted.sort(key=lambda r:r['record_id']);counts=Counter(d['disposition'] for d in dispositions)
    assert sum(counts.values())==len(raw_rows)
    accepted_due=sum(r['orders_due'] for r in accepted);accepted_on_time=sum(r['on_time_orders'] for r in accepted)
    invalid_by_key=Counter(d['record_id'] for d in dispositions if d['disposition']=='QUARANTINED')
    report=dict(version=VERSION,rows_in=len(raw_rows),counts=dict(counts),accepted_unique_keys=len(accepted),quarantined_unique_keys=len(invalid_by_key),normalization_events=len(events),rows_with_normalization=len({e['source_line'] for e in events}),rule_violations=dict(Counter(e['rule'] for e in audit)),accepted_orders_due=accepted_due,accepted_on_time_orders=accepted_on_time,accepted_on_time_rate=accepted_on_time/accepted_due if accepted_due else None,disposition_reconciles=sum(counts.values())==len(raw_rows))
    return {'clean':accepted,'quarantine':quarantine,'row_disposition':dispositions,'transformations':events,'violations':audit,'report':report}

def load_csv(path):
    with path.open(newline='',encoding='utf-8-sig') as f:
        reader=csv.reader(f);header=next(reader,None)
        if header!=FIELDS:raise ValueError('Schema mismatch: headers and order must exactly match the documented contract.')
        for line,row in enumerate(reader,2):
            if len(row)!=len(FIELDS):raise ValueError(f'Malformed CSV row at line {line}. No outputs written.')
    frame=pd.read_csv(path,dtype=str,keep_default_na=False,na_filter=False,encoding='utf-8-sig',skip_blank_lines=False)
    if frame.empty:raise ValueError('Empty feed: at least one data row is required. No outputs written.')
    return frame.to_dict(orient='records')
def csv_safe(value):
    v=text(value)
    # CSV quotes do not stop spreadsheet formula evaluation. Preserve exact raw
    # values separately in raw_evidence.json; prefix only potentially executable text.
    if v.lstrip().startswith(('=','+','-','@','\t','\r')) and not NUMBER.fullmatch(v.strip()):return "'"+v
    return v
def write_csv(path,rows,columns):
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
        for row in rows:writer.writerow({k:csv_safe(row[k]) for k in columns})
def run(input_path,out):
    if out.exists():raise ValueError('Output directory already exists. Choose a new directory to preserve previous runs.')
    raw=load_csv(input_path);result=process(raw)
    result['report']['input_sha256']=hashlib.sha256(input_path.read_bytes()).hexdigest()
    out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent) as tmp:
        stage=Path(tmp)/'result';stage.mkdir()
        columns={'clean':FIELDS,'quarantine':['source_line','reason_codes']+FIELDS,'row_disposition':['source_line','record_id','disposition','reason_codes','duplicate_of_line','raw_row_sha256'],'transformations':['source_line','record_id','field','before','after','final_disposition'],'violations':['source_line','record_id','field','rule','value']}
        for name,cols in columns.items():write_csv(stage/(name+'.csv'),result[name],cols)
        (stage/'raw_evidence.json').write_text(json.dumps(raw,indent=2)+'\n')
        (stage/'report.json').write_text(json.dumps(result['report'],indent=2)+'\n')
        os.rename(stage,out)
    return result['report']
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    try:report=run(args.input,args.output)
    except (ValueError,OSError,pd.errors.ParserError) as exc:parser.exit(2,str(exc)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
