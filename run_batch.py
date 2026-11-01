"""Headless CLI: compute WWZ 16 from a local folder and export results."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
import numpy as np
import json
from gvc import compute_wwz,load_2007_global,reference_comparison

parser=argparse.ArgumentParser(description='WWZ 16-term local batch computation')
parser.add_argument('--input',type=Path,default=Path(__file__).parent/'data/reference_2007')
parser.add_argument('--output',type=Path,default=Path(__file__).parent/'output')
parser.add_argument('--countries',type=int,default=48)
parser.add_argument('--sectors',type=int,default=17)
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
io=load_2007_global(args.input/'2007global.xlsx',args.countries,args.sectors)
r=compute_wwz(io)
np.savez_compressed(args.output/'wwz_results.npz',terms=r.terms,total_exports=r.total_exports,discrepancy=r.discrepancy)
validation={'countries':r.countries,'sectors':r.sectors,'maximum_export_identity_residual':r.max_error(),
            'aggregate_gross_exports':float(r.total_exports.sum())}
if all((args.input/f'T{k}va2007.csv').is_file() for k in range(1,17)):
    validation['matlab_export_comparison']=reference_comparison(r,args.input)
(args.output/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(validation,ensure_ascii=False,indent=2))
