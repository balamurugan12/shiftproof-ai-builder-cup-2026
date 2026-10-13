"""Score category + evidence-set coverage only; semantic scoring remains human work."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import analyze

def match_findings(expected, findings):
    remaining=list(expected)
    matched=0
    for f in findings:
        refs={e['source_id'] for e in f['evidence']}
        match=next((e for e in remaining if e['category']==f['category'] and set(e['source_ids'])==refs),None)
        if match:
            remaining.remove(match)
            matched+=1
    return matched, len(findings)-matched, len(remaining)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['replay','gemini'],default='replay')
    parser.add_argument('--out',default='evaluation/runs/latest.json')
    parser.add_argument('--cases',default=str(Path(__file__).with_name('cases.json')))
    parser.add_argument('--limit',type=int,help='Bound requests for a smoke test; result is marked partial.')
    args=parser.parse_args()
    raw=Path(args.cases).read_bytes()
    cases=json.loads(raw)
    total_cases=len(cases)
    if args.limit is not None:
        if args.limit < 1: parser.error('--limit must be positive')
        cases=cases[:args.limit]
    rows=[];tp=fp=fn=failures=0
    for case in cases:
        try:
            output=analyze(case['sources'],args.mode)
            a,b,c=match_findings(case['expected'],output['report']['findings'])
            tp+=a;fp+=b;fn+=c
            rows.append({'case_id':case['id'],'name':case['name'],'expected':case['expected'],
                         'matched':a,'unmatched_predictions':b,'missed_expected':c,'output':output,
                         'semantic_review':'pending'})
        except Exception as error:
            failures+=1;fn+=len(case['expected'])
            rows.append({'case_id':case['id'],'error_type':type(error).__name__,'semantic_review':'not run'})
    result={'generated_at':datetime.now(timezone.utc).isoformat(),'mode':args.mode,
        'dataset':Path(args.cases).name,
        'dataset_sha256':hashlib.sha256(raw).hexdigest(),
        'annotation_status':'Synthetic draft labels; independent human review required',
        'dataset_total_cases':total_cases,'partial_run':len(cases)<total_cases,
        'metric':'Exact category and evidence-set matching; NOT semantic correctness or business impact',
        'cases':len(cases),'failures':failures,'matched':tp,'unmatched_predictions':fp,'missed_expected':fn,
        'proxy_precision':tp/(tp+fp) if tp+fp else None,'proxy_recall':tp/(tp+fn) if tp+fn else None,
        'rows':rows}
    target=Path(args.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
    if failures: sys.exit(1)
if __name__=='__main__':main()
