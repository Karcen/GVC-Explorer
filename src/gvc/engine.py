"""Faithful vector-level port of WWZ T1..T16 from valueadded2007.m.

The source uses 48 economies (including eight Chinese regions) and 17 industries.
We preserve the original exporter-industry x importer layout in output[t].
The exporter and importer are zero-based indices in Python.
"""
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from scipy.linalg import solve


@dataclass
class IOSystem:
    intermediate: np.ndarray
    final_demand: np.ndarray  # (S*N, S) aggregated across 3 final-demand categories
    value_added: np.ndarray  # (S*N,)
    gross_output: np.ndarray  # (S*N,)
    countries: int
    sectors: int

    def validate(self):
        s, n = self.countries, self.sectors
        m = s*n
        assert self.intermediate.shape == (m,m), f'Z must be ({m},{m})'
        assert self.final_demand.shape == (m,s), f'Y must be ({m},{s})'
        assert self.value_added.shape == (m,)
        assert self.gross_output.shape == (m,)
        for name, v in [('Z',self.intermediate),('Y',self.final_demand),('VA',self.value_added),('X',self.gross_output)]:
            assert np.isfinite(v).all(), f'{name} contains NaN/Inf'
        assert (self.gross_output > 0).all(), 'Gross output must be > 0 for coefficient construction'
        return self


@dataclass
class WWZResult:
    terms: np.ndarray # (16, S*N, S), exporter/industry rows, importer columns
    total_exports: np.ndarray  # (S*N, S)
    discrepancy: np.ndarray  # (S*N, S)
    countries: int
    sectors: int

    def country_totals(self):
        return self.terms.reshape(16,self.countries,self.sectors,self.countries).sum(axis=2)

    def max_error(self):
        m = np.ones((self.countries,self.countries),dtype=bool)
        np.fill_diagonal(m,False)
        d=self.discrepancy.reshape(self.countries,self.sectors,self.countries).transpose(0,2,1)
        return float(np.abs(d[m]).max())


def from_legacy_matrix(G: np.ndarray, countries: int=48, sectors: int=17, final_demand_categories: int=3)->IOSystem:
    """Reproduce the exact MATLAB indexing for Sheet2 of 2007global.xlsx.

    G has first S*N rows as producing sectors; row S*N+1 is VA,
    row S*N+2 is gross input (zero-based). Final demand is after Z.
    """
    s,n = countries,sectors
    m=s*n
    q=final_demand_categories
    assert G.shape[0]>=m+3 and G.shape[1]>=m+s*q, (G.shape,m+3,m+s*q)
    z = np.asarray(G[:m,:m],dtype=np.float64)
    y = np.asarray(G[:m,m:m+s*q],dtype=np.float64).reshape(m,s,q).sum(axis=2)
    va = np.asarray(G[m+1,:m],dtype=np.float64)
    x = np.asarray(G[m+2,:m],dtype=np.float64)
    return IOSystem(z,y,va,x,s,n).validate()


def compute_wwz(io:IOSystem, progress=None)->WWZResult:
    """Vector-for-vector translation of valueadded2007.m lines 12-549.

    Uses SciPy's solve for the Leontief inverse, which is mathematically
    identical to the MATLAB right division I/(I-A) for these matrices.
    """
    io.validate()
    S,N=io.countries,io.sectors
    M=S*N
    if progress:progress('Constructing Leontief matrices',0.05)
    a=io.intermediate/io.gross_output[None,:]
    v=io.value_added/io.gross_output
    B=solve(np.eye(M)-a,np.eye(M),assume_a='gen',check_finite=True)
    ab=a.reshape(S,N,S,N).transpose(0,2,1,3)
    bb=B.reshape(S,N,S,N).transpose(0,2,1,3)
    y=io.final_demand.reshape(S,N,S).transpose(0,2,1)
    lv=np.empty((S,N,N))
    for i in range(S):
        lv[i]=solve(np.eye(N)-ab[i,i],np.eye(N),assume_a='gen')
    vv=v.reshape(S,N)
    total_final = y.sum(axis=1)
    # Direct intermediate exports, excluding domestic transfers; axis i,j,industry.
    de=io.intermediate.reshape(S,N,S,N).transpose(0,2,1,3).sum(axis=3)
    te=(de+y).sum(axis=1)-(de[np.arange(S),np.arange(S)]+y[np.arange(S),np.arange(S)])
    exp=de+y
    exp[np.arange(S),np.arange(S)]=0
    if progress:progress('Computing final-demand contractions',0.25)
    # Precompute repeated block products of the original tt2..tt9 MATLAB code.
    diagY=y[np.arange(S),np.arange(S)] # (S,N)
    b_diag=np.einsum('jtab,ta->jb',bb,diagY,optimize=True) # output indices? jtab: (j,t,a,b), input t,b -> j,a
    b_diag=np.einsum('jtab,tb->ja',bb,diagY,optimize=True)
    b_to=np.einsum('jtab,tib->jia',bb,y,optimize=True) # (j,i, industry at j)
    b_export_final=np.einsum('jtab,tb->ja',bb,total_final-diagY,optimize=True)
    vb_own=np.einsum('ia,iab->ib',vv,bb[np.arange(S),np.arange(S)],optimize=True)
    vl_own=np.einsum('ia,iab->ib',vv,lv,optimize=True)
    vB_all = v @ B
    vB_blocks=vB_all.reshape(S,N)
    result=np.zeros((16,S,N,S),dtype=np.float64)
    for i in range(S):
        if progress and i%max(1,S//8)==0:progress('Decomposing bilateral exports',0.35+0.6*i/S)
        for j in range(S):
            if i==j: continue
            aij=ab[i,j]
            bjj=bb[j,j]
            bji=bb[j,i]
            yii=diagY[i]
            yjj=diagY[j]
            yij=y[i,j]
            yji=y[j,i]
            # MATLAB's eight terms for gross intermediate exports (tt2...tt9)
            tt2=aij@(bjj@yjj)
            tt3=aij@(b_diag[j]-bji@yii-bjj@yjj)
            tt4=aij@(bjj@(total_final[j]-yji-yjj))
            # Exclude third-country index t=i,j from tt5.
            removal_i=bji@(total_final[i]-y[i,i]-y[i,i])
            removal_j=bjj@(total_final[j]-y[j,i]-y[j,j])
            tt5=aij@(b_export_final[j]-b_to[j,i]-removal_i-removal_j)
            tt6=aij@(bjj@yji)
            tt7=aij@(b_to[j,i]-bjj@yji-bji@yii)
            tt8=aij@(bji@yii)
            tt9=aij@(bji@(total_final[i]-yii))
            # Faithful formulas from lines 281-519 (MATLAB index 1..16).
            result[0,i,:,j]=vb_own[i]*yij
            for k,t in enumerate((tt2,tt3,tt4,tt5,tt6,tt7,tt8,tt9),start=1):
                result[k,i,:,j]=vl_own[i]*t
            result[9,i,:,j]=(vb_own[i]-vl_own[i])*de[i,j]
            foreign_j=vv[j]@bji
            result[10,i,:,j]=foreign_j*yij
            backward=aij@(lv[j]@yjj)
            backward_export=aij@(lv[j]@te[j])
            result[11,i,:,j]=foreign_j*backward
            result[12,i,:,j]=foreign_j*backward_export
            other=vB_blocks[i]-vb_own[i]-foreign_j
            result[13,i,:,j]=other*yij
            result[14,i,:,j]=other*backward
            result[15,i,:,j]=other*backward_export
    terms=result.reshape(16,M,S)
    total=exp.transpose(0,2,1).reshape(M,S)
    discrepancy=total-terms.sum(axis=0)
    if progress:progress('WWZ computation finished',1.0)
    return WWZResult(terms,total,discrepancy,S,N)


def reference_comparison(result:WWZResult,folder:Path)->dict:
    """Compare each result to MATLAB-exported CSV (5-6 significant digits).
    CSV layout is 816 rows by 48 importers; diagonal blocks are all zero.
    """
    checks={}
    for term in range(16):
        path=folder/f'T{term+1}va2007.csv'
        ref=np.loadtxt(path,delimiter=',')
        assert ref.shape==result.terms[term].shape,(path,ref.shape,result.terms[term].shape)
        err=np.abs(result.terms[term]-ref)
        scale=np.maximum(np.abs(ref),1)
        checks[f'T{term+1}']={
            'max_absolute_error':float(err.max()),
            'max_relative_to_unit_scale':float((err/scale).max()),
            'mean_absolute_error':float(err.mean()),
        }
    return checks
