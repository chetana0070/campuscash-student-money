import argparse, datetime as dt, json, sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

def amount(v):
    try:
        x=Decimal(str(v))
        if not x.is_finite() or abs(x)>100000000: raise ValueError()
        return x.quantize(Decimal('.01'))
    except (InvalidOperation,ValueError,TypeError): raise ValueError('Invalid monetary amount')

def forecast(data,days=30):
    if not 1<=days<=90: raise ValueError('days must be 1..90')
    if data.get('currency','USD')!='USD': raise ValueError('USD only')
    start=dt.date.fromisoformat(data['as_of']); balance=amount(data['starting_balance']); buffer=amount(data.get('minimum_buffer','100'))
    if buffer<0: raise ValueError('Negative buffer')
    events=data.get('events',[])
    if not isinstance(events,list) or len(events)>1000: raise ValueError('Invalid events')
    parsed=[]
    for e in events:
        d=dt.date.fromisoformat(e['date']); a=amount(e['amount']); status=e.get('status','expected')
        if status not in ('confirmed','expected','planned'): raise ValueError('Invalid status')
        parsed.append((d,a,status,str(e.get('label','Event'))[:80]))
    low=stress_low=balance; low_date=start; stress_balance=balance; first_negative=None; first_below=None; stress_negative=None
    for offset in range(days):
        date=start+dt.timedelta(days=offset)
        today=[e for e in parsed if e[0]==date]
        for _,a,status,_ in today:
            balance+=a
            if a<0 or status=='confirmed': stress_balance+=a
        if balance<low: low,low_date=balance,date
        stress_low=min(stress_low,stress_balance)
        if first_negative is None and balance<0: first_negative=date
        if first_below is None and balance<buffer: first_below=date
        if stress_negative is None and stress_balance<0: stress_negative=date
    fmt=lambda v: format(v,'.2f')
    when=lambda d:d.isoformat() if d else None
    risk='SHORTFALL' if first_negative else 'LOW_BUFFER' if first_below else 'ON_TRACK'
    return {'as_of':when(start),'through':when(start+dt.timedelta(days=days-1)),'currency':'USD','starting_balance':fmt(amount(data['starting_balance'])),'minimum_buffer':fmt(buffer),'projected_end_balance':fmt(balance),'lowest_projected_balance':fmt(low),'lowest_balance_date':when(low_date),'first_negative_date':when(first_negative),'first_below_buffer_date':when(first_below),'risk':risk,'without_unconfirmed_income_scenario':{'lowest_balance':fmt(stress_low),'first_negative_date':when(stress_negative)},'upcoming_expenses':[{'date':when(d),'label':label,'amount':fmt(-a)} for d,a,_,label in sorted(parsed) if start<=d<start+dt.timedelta(days=days) and a<0],'caveat':'Scenario based on entered amounts; expected income and posting order are not guaranteed.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(); mx=p.add_mutually_exclusive_group(required=True); mx.add_argument('--input'); mx.add_argument('--sample',action='store_true'); p.add_argument('--days',type=int,default=30); args=p.parse_args()
    try:
        path=Path(__file__).resolve().parents[1]/'assets'/'demo.json' if args.sample else Path(args.input)
        print(json.dumps(forecast(json.loads(path.read_text(encoding='utf8')),args.days),indent=2))
    except (ValueError,KeyError,OSError,json.JSONDecodeError) as ex:
        print(f'ERROR: {ex}',file=sys.stderr); sys.exit(2)
