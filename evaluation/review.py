"""Export a blank human review sheet from a recorded run; never auto-label meaning."""
import argparse
import csv
import json
from pathlib import Path

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('run')
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    run=json.loads(Path(args.run).read_text())
    target=Path(args.out);target.parent.mkdir(parents=True,exist_ok=True)
    fields=['case_id','finding_id','category','observation','evidence_json','expected_json','supported_yes_no','required_missing_yes_no','unsafe_instruction_yes_no','reviewer','rationale']
    with target.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for row in run['rows']:
            findings=row.get('output',{}).get('report',{}).get('findings',[])
            for finding in findings or [{}]:
                writer.writerow({'case_id':row['case_id'],'finding_id':finding.get('id','NO_FINDINGS_OR_ERROR'),'category':finding.get('category',''),'observation':finding.get('observation',''),'evidence_json':json.dumps(finding.get('evidence',[])),'expected_json':json.dumps(row.get('expected',[]))})
    print(target)

if __name__=='__main__':main()
