"""One local run: account, reconcile, render, and commit a new results directory."""
from pathlib import Path
from importlib.resources import files
from tempfile import TemporaryDirectory
from uuid import uuid4
from datetime import datetime
import base64,json,sys,platform
import numpy as np
import matplotlib, scipy
from plotly.offline import get_plotlyjs
from .studio_io import load_input,catalog,digest
from .engine import compute_wwz,WWZResult
from .atlas import GROUPS,GN,TC,TITLE,IDS,COL,default_view,export_atlas

def result_at(p,m):
    with np.load(p,allow_pickle=False) as z:return WWZResult(z['terms'],z['total_exports'],z['discrepancy'],len(m['areas']),len(m['sectors']))

def save_html(path,r,m,view,lang='zh'):
    def encode(x):return base64.b64encode(np.ascontiguousarray(x,dtype='<f8')).decode('ascii')
    bundle=dict(terms=encode(r.terms),gross=encode(r.total_exports),meta=m,residual=r.max_error(),groups=GROUPS,gnames=GN,termcodes=TC,titles=TITLE,ids=IDS,colors=COL,view=[view.exporter,view.importer,view.sector,view.term],lang=lang,catalog=catalog('icio_display'))
    w=files('gvc').joinpath('web');html=w.joinpath('template.html').read_text(encoding='utf-8').replace('__CSS__',w.joinpath('design.css').read_text(encoding='utf-8')).replace('__APP__',w.joinpath('app.js').read_text(encoding='utf-8')).replace('__PLOTLY__',get_plotlyjs()).replace('__DATA__',json.dumps(bundle,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('<','\\u003c'))
    Path(path).write_text(html,encoding='utf-8')

def run(path,parent,lang='zh',member=None,progress=lambda stage,p:None):
    parent=Path(parent);parent.mkdir(parents=True,exist_ok=True);progress('read',1);io,m=load_input(Path(path),member);progress('solve',10)
    r=compute_wwz(io,lambda _,p:progress('solve',10+int(48*p)));del io
    error=r.max_error();margin=.10+1e-4*np.abs(r.total_exports) if m.get('layout')=='ICIO national block' else 1e-7+1e-7*np.abs(r.total_exports)
    if not np.isfinite(r.terms).all() or np.any(np.abs(r.discrepancy)>margin):raise ValueError(f'WWZ reconciliation failed / 分解合计不等于总出口: max |Δ|={error:.8g}')
    view=default_view(r,m);target=parent/(datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid4().hex[:8]);
    with TemporaryDirectory(dir=parent,prefix='.in-progress-') as tmp:
        p=Path(tmp)/'run';p.mkdir();progress('save',60);np.savez_compressed(p/'results.npz',terms=r.terms,total_exports=r.total_exports,discrepancy=r.discrepancy)
        (p/'metadata.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');progress('figures',65);export_atlas(r,m,view,lang,p/'figures');progress('html',90);save_html(p/'atlas.html',r,m,view,lang);manifest={'input':m['source'],'input_sha256':m['sha256'],'economic_unit':m['unit'],'basis':m['basis'],'year':m.get('year'),'dimensions':[r.countries,r.sectors],'max_abs_export_residual':error,'gross_exports':float(r.total_exports.sum()),'diagnostics':m.get('diagnostics',{}),'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__},'files':{str(q.relative_to(p)):digest(q) for q in sorted(p.rglob('*')) if q.is_file()}};(p/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8');p.rename(target)
    progress('done',100);return target
