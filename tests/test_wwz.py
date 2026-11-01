from pathlib import Path
import numpy as np
from gvc import IOSystem,compute_wwz,load_2007_global,reference_comparison

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'data'/'reference_2007'

def test_toy_accounting_identity():
    rng=np.random.default_rng(42)
    S,N=3,2
    m=S*N
    A=rng.uniform(0.002,0.04,size=(m,m))
    Y=rng.uniform(5,15,size=(m,S))
    x=np.linalg.solve(np.eye(m)-A,Y.sum(axis=1))
    Z=A*x[None,:]
    VA=x-Z.sum(axis=0)
    result=compute_wwz(IOSystem(Z,Y,VA,x,S,N))
    assert np.isclose(result.terms.sum(),result.total_exports.sum(),rtol=1e-12,atol=1e-10)
    assert result.max_error()<1e-10
    assert result.terms.shape==(16,m,S)
    for i in range(S):
        assert (result.terms[:,i*N:(i+1)*N,i]==0).all()

def test_original_matlab_csv_parity():
    io=load_2007_global(REF/'2007global.xlsx')
    result=compute_wwz(io)
    assert result.max_error()<1e-7
    checks=reference_comparison(result,REF)
    assert len(checks)==16
    # Original CSV files use approximately five significant digits; not exact doubles.
    assert max(c['max_relative_to_unit_scale'] for c in checks.values())<5.2e-5

def test_original_reference_shape():
    for k in range(1,17):
        assert np.loadtxt(REF/f'T{k}va2007.csv',delimiter=',').shape==(816,48)
