"""Command-line equivalent of a desktop analysis; no GUI or network required."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from gvc.studio_run import run
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--output',type=Path,default=Path('runs'));p.add_argument('--language',choices=['en','zh'],default='zh');p.add_argument('--member',help='Exact CSV member name inside a multi-year ZIP');args=p.parse_args()
    out=run(args.input,args.output,args.language,args.member,lambda stage,percent:print(json.dumps(dict(stage=stage,percent=percent)),flush=True));print(json.dumps({'directory':str(out.resolve())}),flush=True)
