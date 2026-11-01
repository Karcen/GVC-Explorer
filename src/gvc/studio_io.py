"""Read labelled annual ICIO transactions. Keys, never row positions, define a new table."""
from __future__ import annotations
import csv, gzip, hashlib, io, json, re, zipfile
from pathlib import Path, PurePosixPath
from contextlib import contextmanager
from importlib.resources import files
import numpy as np
import pandas as pd
from .engine import IOSystem
from .loaders import load_2007_global
from .metadata import resolve_labels

FD={'HFCE','NPISH','GGFC','GFCF','INVNT','DPABR'}
NORM_FD={'DIRPA':'DPABR','DPABROAD':'DPABR'}
def catalog(name):return json.loads(files('gvc').joinpath('data',name+'.json').read_text(encoding='utf-8'))
def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for piece in iter(lambda:f.read(1<<20),b''):h.update(piece)
    return h.hexdigest()
def balance(label,actual,expected,atol=0.10,rtol=1e-5):
    diff=np.abs(actual-expected); lim=atol+rtol*np.abs(expected)
    if np.any(diff>lim):
        k=int(np.argmax(diff/lim)); raise ValueError(f'{label}: {k+1}, |Δ|={diff[k]:.6g}, tolerance={lim[k]:.6g}. 核对总产出、税项及最终需求 / Check output, taxes and final demand.')
    return float(diff.max())

def read_annual(f,source,sha):
    header=next(csv.reader(f));header=[v.strip() for v in header];f.seek(0)
    if len(set(header[1:]))!=len(header)-1:raise ValueError('重复列代码 / Duplicate column codes')
    if len(header)>15000:raise ValueError('Too many columns / 列数超出支持范围')
    tab=pd.read_csv(f,index_col=0,low_memory=False);tab.columns=header[1:];tab.index=tab.index.astype(str).str.strip()
    if not tab.index.is_unique:raise ValueError('重复行代码 / Duplicate row codes')
    special={'TLS','VA','VALU','OUT','OUTPUT'}; rows=[r for r in tab.index if r not in special]; keys=[i.split('_',1) for i in rows]
    if not rows or not all(len(k)==2 for k in keys):raise ValueError('需要经济体_行业表头 / Expected AREA_ACTIVITY row keys and VA, OUT')
    display=catalog('icio_display'); amap=display['areas']; smap=display['sectors']; aliases={v['alias']:k for k,v in smap.items()};aliases.update({'D86T89':'Q','D17_18':'C17_18','D62_63':'J62_63'})
    areas=list(dict.fromkeys(k[0] for k in keys)); secs=list(dict.fromkeys(k[1] for k in keys));S=len(areas);N=len(secs)
    if set(areas)-set(amap):raise ValueError('Unknown area / 未知经济体: '+str(sorted(set(areas)-set(amap))))
    mapped=[aliases.get(c,c) for c in secs]
    if set(mapped)-set(smap) or len(set(mapped))!=N:raise ValueError('Unsupported or mixed industry classification / 不支持或混用行业分类: '+str(secs))
    full=[f'{a}_{s}' for a in areas for s in secs]
    if set(full)!=set(rows) or not set(full)<=set(tab.columns):raise ValueError('不完整的交易矩阵 / Incomplete rectangular Z block or mismatched keys')
    # National perspective only: never count both consolidated China/Mexico and their components.
    splits={'CN1':'CHN','CN2':'CHN','MX1':'MEX','MX2':'MEX'};dropped=[a for a in areas if a in splits]
    if any(splits[a] not in areas for a in dropped):raise ValueError('仅有生产拆分项，缺少国家合计 / National totals required for a split-area table')
    areas=[a for a in areas if a not in splits];S=len(areas)
    if S<2:raise ValueError('At least two distinct economies / 至少两个经济体')
    ids=[f'{a}_{s}' for a in areas for s in secs]; M=len(ids)
    va_names=[i for i in ('VA','VALU') if i in tab.index];x_names=[i for i in ('OUT','OUTPUT') if i in tab.index];out_cols=[i for i in ('OUT','OUTPUT') if i in tab.columns]
    if not(len(va_names)==len(x_names)==len(out_cols)==1):raise ValueError('需要唯一的 VA 行、OUT 行及 OUT 列 / Expected one VA row, output row and output column')
    fd_by={a:{} for a in areas}
    for c in tab.columns.difference(full+out_cols):
        pair=c.split('_',1)
        if len(pair)!=2 or NORM_FD.get(pair[1],pair[1]) not in FD or pair[0] not in fd_by:raise ValueError('Unknown final demand / 未知最终需求列: '+c)
        a,k=pair;k=NORM_FD.get(k,k)
        if k in fd_by[a]:raise ValueError('Duplicate final demand category: '+c)
        fd_by[a][k]=c
    for a,columns in fd_by.items():
        if set(columns)!=FD:raise ValueError(f'{a}: missing final-demand categories / 缺少最终需求类别 {sorted(FD-set(columns))}')
    def block(rr,cc):
        x=tab.loc[rr,cc].to_numpy(dtype='float64');
        if not np.isfinite(x).all():raise ValueError('交易区含缺失或无穷值 / Missing or non-finite transaction value; do not fill blanks with zero')
        return x
    z=block(ids,ids);y=np.column_stack([block(ids,list(fd_by[a].values())).sum(axis=1) for a in areas]);x=block(x_names,ids)[0];out=block(ids,out_cols).ravel();v=block(va_names,ids)[0];tls=block(['TLS'],ids)[0] if 'TLS' in tab.index else np.zeros_like(x)
    diag={'row_vs_column_output':balance('OUT row/column',out,x),'sales_balance':balance('Z·1 + Y·1 = X',z.sum(axis=1)+y.sum(axis=1),x),'cost_balance':balance('1′Z + VA + TLS = X',z.sum(axis=0)+v+tls,x),'structural_zero_outputs':int((x==0).sum()),'taxes_less_subsidies_sum':float(tls.sum()),'max_abs_tax':float(np.abs(tls).max()),'dropped_split_series':dropped,'ignored_domestic_as_exports':True}
    matches=re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',Path(source).stem); year=int(matches[0]) if len(matches)==1 else None
    meta=dict(source=source,sha256=sha,year=year,unit='USD million',basis='VA+TLS' if np.any(tls) else 'VA',areas=[amap[a] for a in areas],sectors=[dict(smap[m],code=c) for m,c in zip(mapped,secs)],diagnostics=diag,layout='ICIO national block',fixture='fixture' in source.lower())
    return IOSystem(z,y,v+tls,x,S,N).validate(),meta

def load_input(path:Path,member=None):
    path=Path(path)
    if path.is_dir():
        meta=json.loads((path/'metadata.json').read_text(encoding='utf-8-sig')); y=np.loadtxt(path/'Y.csv',delimiter=',',ndmin=2);m,s=y.shape
        if s<2 or m%s:raise ValueError('Y shape / Y 维度错误')
        n=m//s; names,inds,src=resolve_labels(meta,s,n)
        if 'Unverified' in src:raise ValueError('metadata.json: provide country_names and industry_names in matrix order / 必须提供有序名称')
        def named(names):return [dict(code=str(k+1),en=t,zh=t) for k,t in enumerate(names)]
        a,b=named(names),named(inds)
        if meta.get('classification')=='OECD_ICIO_2025_EXTENDED':raise ValueError('Use the labelled annual CSV to exclude duplicate national and split components / 请导入带表头的年度 CSV')
        sys=IOSystem(np.loadtxt(path/'Z.csv',delimiter=',',ndmin=2),y,np.loadtxt(path/'VA.csv',delimiter=',').reshape(-1),np.loadtxt(path/'X.csv',delimiter=',').reshape(-1),s,n).validate();diag={'sales_balance':balance('Sales',sys.intermediate.sum(1)+y.sum(1),sys.gross_output),'cost_balance':balance('Costs',sys.intermediate.sum(0)+sys.value_added,sys.gross_output)}
        return sys,dict(source=path.name,sha256={f:digest(path/f) for f in ['Z.csv','Y.csv','VA.csv','X.csv','metadata.json']},year=meta.get('year'),unit=meta.get('unit') or 'input units',areas=a,sectors=b,basis='VA',layout='canonical',diagnostics=diag)
    sha=digest(path);suffix=path.suffix.lower()
    if suffix=='.xlsx':
        meta=catalog('legacy_axes')
        if sha!=meta['sha256']:raise ValueError('XLSX 仅支持已核验的 2007 基准表。其他表请使用带表头的年度 CSV。 / Use a labelled annual CSV for other workbooks.')
        return load_2007_global(path),meta
    if suffix=='.zip':
        with zipfile.ZipFile(path) as z:
            options=annual_members(z)
            if member is None and len(options)==1:member=options[0]
            if member not in options:raise ValueError('请选择一个年度 CSV / Choose one annual CSV: '+', '.join(options))
            with z.open(member) as b,io.TextIOWrapper(b,encoding='utf-8-sig',newline='') as f: sys,meta=read_annual(f,PurePosixPath(member).name,sha)
            meta['archive_member']=member;meta['archive']=path.name;return sys,meta
    if suffix not in {'.csv','.gz'}:raise ValueError('Supported: annual CSV, CSV.GZ, ZIP, reference XLSX or canonical directory')
    op=gzip.open if suffix=='.gz' else open
    with op(path,'rt',encoding='utf-8-sig',newline='') as f:return read_annual(f,path.name,sha)

def annual_members(z):
    entries=[i for i in z.infolist() if i.filename.lower().endswith('.csv') and not i.filename.startswith('__MACOSX/')]; names=[i.filename for i in entries]
    if len(names)!=len(set(names)) or any(i.file_size>1_500_000_000 for i in entries):raise ValueError('ZIP has duplicate or excessively large CSV members / ZIP 成员重复或过大')
    return names
