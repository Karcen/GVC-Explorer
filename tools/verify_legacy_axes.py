from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
P=Path(__file__).resolve().parents[1];N='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def walk(p,sheet):
 with ZipFile(p) as z:
  ss=[''.join(s.itertext()) for s in E.fromstring(z.read('xl/sharedStrings.xml'))];w=E.fromstring(z.read('xl/workbook.xml'));rels={r.get('Id'):r.get('Target') for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))};sh=next(s for s in w.iter(N+'sheet') if s.get('name')==sheet);f=z.open('xl/'+rels[sh.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]);
  for _,r in E.iterparse(f,events=('end',),tag=N+'row'):
   a={}
   for c in r.iter(N+'c'):
    v=c.findtext(N+'v');
    if v is not None:a[c.get('r')]=(ss[int(v)] if c.get('t')=='s' else float(v))
   yield int(r.get('r')),a;r.clear();
   while r.getprevious() is not None:del r.getparent()[0]
import numpy as np, json, hashlib

def letter(i):
 s=''
 while i: i,r=divmod(i-1,26);s=chr(65+r)+s
 return s

def verify(p):
 h=walk(p,'Sheet1');heads=[next(h)[1] for _ in range(5)];b=walk(p,'Sheet2');a,s=[],[];c1=[letter(i+6) for i in range(960)];c2=[letter(i+1) for i in range(960)];mx=np.zeros(4);n=np.zeros(4,int)
 for k in range(816):
  r,v=next(h);j,w=next(b);assert r==k+6 and j==k+1
  area=v[f'C{r}'];sector=v[f'D{r}'];assert (v[f'A{r}'],v[f'B{r}'],v[f'E{r}'])==(1+k//17,k+1,1+k%17)
  if k%17==0:a.append(area)
  if k<17:s.append(sector)
  assert a[k//17]==area==heads[2][c1[k]+'3'] and s[k%17]==sector==heads[3][c1[k]+'4']
  d=np.array([w[c+str(j)]-v[t+str(r)] for c,t in zip(c2,c1)]);groups=[d[:816],d[816::3],d[817::3],d[818::3]];mx=np.maximum(mx,[np.abs(q).max() for q in groups]);n +=[np.count_nonzero(q) for q in groups]
 assert len(set(a))==48 and len(set(s))==17 and not n.any(), mx
 for k,c in enumerate(c1[816:]):assert heads[3][c+'4']==a[k//3] and heads[0][c+'1']==k//3+1
 return dict(workbook_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source='Sheet1!C6:D821, rows 3–4 and C4; Sheet2 numeric input',unit=heads[3]['C4'],axes=a,sectors=s,compared_Z_cells=816**2,compared_FD_cells=816*144,max_abs_Z_FD1_FD2_FD3=mx.tolist(),nonidentical_Z_FD1_FD2_FD3=n.tolist())
if __name__=='__main__':
 rec=verify(P/'data/reference_2007/2007global.xlsx');(P/'reports/legacy_axis_audit.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));print(rec)
