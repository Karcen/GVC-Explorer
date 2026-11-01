"""Exercise supported input layouts, explicit accounting choices, and shape-preserving reindexing."""
from pathlib import Path
from io import StringIO
from zipfile import ZipFile
import gzip, json
import numpy as np
import pandas as pd
import pytest
from gvc.studio_io import load_input, read_annual, catalog
from gvc.engine import compute_wwz,IOSystem
from gvc.atlas import sourceview, View
ROOT=Path(__file__).resolve().parents[1]; EX=ROOT/'examples/fixture_3area_3sector.csv'
def frame(): return pd.read_csv(EX,index_col=0)
def read(t): return read_annual(StringIO(t.to_csv()),'fixture_2020.csv','test')

def test_tax_final_demand_and_named_axes():
    system,m=load_input(EX);assert (system.countries,system.sectors)==(3,3);assert [v['code'] for v in m['areas']]==['AUS','DEU','JPN'];assert m['sectors'][1]['code']=='C26';assert m['basis']=='VA+TLS';assert m['fixture'];assert system.final_demand[0,0]==52+43+11+57-2+6;raw=frame();assert np.allclose(system.value_added, raw.loc['VA'].iloc[:9]+raw.loc['TLS'].iloc[:9]);assert compute_wwz(system).max_error()<2e-12

def test_permuted_columns_and_rows():
    orig=frame();system,m=read(orig);r=compute_wwz(system);perm=orig.sample(frac=1,axis=1,random_state=7).sample(frac=1,axis=0,random_state=3); new,n=read(perm);r2=compute_wwz(new)
    for a,area in enumerate(m['areas']):
        aa=n['areas'].index(area)
        for k,sec in enumerate(m['sectors']):
            kk=n['sectors'].index(sec)
            for b,partner in enumerate(m['areas']):np.testing.assert_allclose(r.terms[:,a*3+k,b],r2.terms[:,aa*3+kk,n['areas'].index(partner)],atol=1e-11)

def test_bad_column_and_missing_data():
    t=frame();t.columns=[t.columns[0],*t.columns[:-1]]
    with pytest.raises(ValueError,match='Duplicate'):read(t)
    with pytest.raises(ValueError,match='missing final-demand'):read(frame().drop(columns='AUS_NPISH'))
    t=frame();t.loc['AUS_A01','DEU_A01']=float('nan')
    with pytest.raises(ValueError,match='non-finite'):read(t)

def test_unbalanced_input_and_unrecognized_classification():
    t=frame();t.loc['VA','AUS_A01']+=1
    with pytest.raises(ValueError,match='VA'):read(t)
    with pytest.raises(ValueError,match='industry'):read(frame().rename(index={'DEU_A01':'DEU_XYZ'}))

def test_no_double_counting_china():
    t=frame();t.index=[x.replace('AUS','CHN') for x in t.index];t.columns=[x.replace('AUS','CHN') for x in t.columns];original,_=read(t)
    for s in ['A01','C26','K']: t['CN1_'+s]=t['CHN_'+s]
    for s in ['A01','C26','K']:t.loc['CN1_'+s]=t.loc['CHN_'+s]
    w,m=read(t);np.testing.assert_array_equal(original.intermediate,w.intermediate);assert m['diagnostics']['dropped_split_series']==['CN1'];assert w.countries==3
    t=t.drop(index=['CHN_A01','CHN_C26','CHN_K'])
    with pytest.raises(ValueError,match='National totals'):read(t)

def test_gzip_and_multiyear_selection(tmp_path):
    with gzip.open(tmp_path/'2020.csv.gz','wb') as f:f.write(EX.read_bytes())
    s,m=load_input(tmp_path/'2020.csv.gz');assert m['year']==2020
    p=tmp_path/'pack.zip'
    with ZipFile(p,'w') as z:z.write(EX,'years/2021.csv');z.write(EX,'years/2022.csv')
    with pytest.raises(ValueError,match='Choose one'):load_input(p)
    o,n=load_input(p,'years/2022.csv');assert n['year']==2022 and n['archive_member']=='years/2022.csv';np.testing.assert_array_equal(o.final_demand,s.final_demand)

def test_structural_zeros_are_not_filled_with_transactions():
    io=IOSystem(np.zeros((2,2)),np.array([[1.,2.],[0,0]]),np.array([3.,0]),np.array([3.,0]),2,1);assert compute_wwz(io).max_error()==0;io.intermediate[0,1]=.1
    with pytest.raises(ValueError,match='Zero output'):io.validate()

def test_same_basis_under_both_display_languages():
    sys,m=load_input(EX);r=compute_wwz(sys);views=[sourceview(r,m,View(1,2,-1,5),lang) for lang in ('zh','en')];
    for a,b in zip(*views):np.testing.assert_array_equal(a['values'],b['values']);assert a['title']!=b['title']
    spec=views[0];assert len(spec)==8;assert np.isclose(spec[1]['values'].sum(),spec[0]['values'].sum());assert np.isclose(spec[5]['values'][0],spec[0]['values'].sum());assert len(catalog('legacy_axes')['areas'])==48

def test_offline_formula_handbooks_are_script_free():
    from lxml import html
    for lang in ('zh','en'):
        d=html.parse(ROOT/f'docs/formulas_{lang}.html');assert len(d.xpath('//*[@class="equation"]'))==17;assert len(d.xpath('//*[@class="inline"]'))>=40;assert not d.xpath('//script|//*[@data-mml-node="merror"]');assert not d.xpath('//*[@src]')
