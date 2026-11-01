"""Local-only importers for MATLAB-era and general IO exchange files."""
from pathlib import Path
from zipfile import ZipFile
import re
import numpy as np
from lxml import etree
from .engine import from_legacy_matrix

_NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
_REL='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

def read_numeric_xlsx(path:Path, sheet:str='Sheet2', max_rows:int|None=None,max_cols:int|None=None)->np.ndarray:
    """Memory-bounded XLSX worksheet reader using Office Open XML.

    Numeric cells only; formula cached values accepted. Rejects missing values
    in the selected rectangle rather than silently filling with zero.
    """
    with ZipFile(path) as z:
        root=etree.fromstring(z.read('xl/workbook.xml'))
        names={sh.get('name'):sh.get(_REL+'id') for sh in root.find(_NS+'sheets')}
        assert sheet in names,f'{sheet} not in workbook ({list(names)})'
        rels=etree.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets={r.get('Id'):r.get('Target') for r in rels}
        target=targets[names[sheet]].lstrip('/')
        if not target.startswith('xl/'):
            target='xl/'+target
        values={}
        max_r=max_c=0
        with z.open(target) as f:
            for _,row in etree.iterparse(f, events=('end',),tag=_NS+'row'):
                r=int(row.get('r'))-1
                if max_rows is not None and r>=max_rows:
                    row.clear()
                    while row.getprevious() is not None:del row.getparent()[0]
                    continue
                for cell in row.iter(_NS+'c'):
                    ref=cell.get('r')
                    letters=re.match(r'[A-Z]+',ref).group()
                    c=0
                    for letter in letters:c=c*26+ord(letter)-64
                    c-=1
                    if max_cols is not None and c>=max_cols: continue
                    v=cell.find(_NS+'v')
                    if v is None:continue
                    if cell.get('t') not in (None,'n'):
                        raise ValueError(f'Non-numeric cell {ref} in {sheet}')
                    values[(r,c)]=float(v.text)
                    max_c=max(max_c,c+1)
                max_r=max(max_r,r+1)
                row.clear()
                while row.getprevious() is not None:del row.getparent()[0]
    rows=max_rows or max_r
    cols=max_cols or max_c
    out=np.full((rows,cols),np.nan,dtype=np.float64)
    for (r,c),v in values.items():out[r,c]=v
    return out

def load_2007_global(path:Path,countries:int=48,sectors:int=17):
    m=countries*sectors
    g=read_numeric_xlsx(path,'Sheet2',m+3,m+3*countries)
    # Historical workbook may have sparse unlabeled rows; only used slices matter.
    return from_legacy_matrix(g,countries,sectors)

def load_reference_terms(folder:Path,countries:int=48,sectors:int=17):
    mats=[]
    for term in range(1,17):
        p=folder/f'T{term}va2007.csv'
        assert p.exists(),f'Missing {p.name}'
        arr=np.loadtxt(p,delimiter=',')
        assert arr.shape==(countries*sectors,countries),(p.name,arr.shape)
        mats.append(arr)
    return np.stack(mats)
