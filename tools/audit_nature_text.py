"""Run the reviewed nature-figure text auditor locally. No network activity."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
BLOB='10830f22870fe00f365df3989e0af56e6481cb21'

def run(script,figdir):
    code=script.read_bytes();blob=hashlib.sha1(b'blob '+str(len(code)).encode()+b'\0'+code).hexdigest()
    if blob!=BLOB:raise ValueError('Auditor differs from the reviewed Git object: '+blob)
    result=[]
    for file in sorted(figdir.rglob('*.pdf')):
        proc=subprocess.run([sys.executable,'-I',str(script),str(file),'--min-pt','6.5','--json'],capture_output=True,text=True,check=True);rec=json.loads(proc.stdout);rec['pdf']=str(file.relative_to(figdir));result.append(rec)
    if not result:raise ValueError('No PDF figures in '+str(figdir))
    return {'source':'Yuan1z0825/nature-skills:skills/nature-figure/scripts/audit_pdf_text.py','git_blob':blob,'results':result}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('script',type=Path);p.add_argument('figures',type=Path);p.add_argument('--output',required=True,type=Path);args=p.parse_args();out=run(args.script,args.figures);args.output.write_text(json.dumps(out,indent=2),encoding='utf-8');print(f"{len(out['results'])} PDFs passed")
