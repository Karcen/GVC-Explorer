import numpy as np,csv
from pathlib import Path
S,N=3,3; A=['AUS','DEU','JPN'];sec=['A01','C26','K'];ids=[a+'_'+s for a in A for s in sec];fd=['HFCE','NPISH','GGFC','GFCF','INVNT','DPABR'];cols=[a+'_'+k for a in A for k in fd];m=len(ids);r=np.random.default_rng(551);z=r.integers(1,55,(m,m));y=r.integers(1,60,(m,len(cols)));y[:,4]=-2;x=z.sum(1)+y.sum(1);t=np.arange(1,m+1);v=x-z.sum(0)-t
with open('examples/fixture_3area_3sector.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['activity']+ids+cols+['OUT']);w.writerows([k,*z[i],*y[i],x[i]] for i,k in enumerate(ids));w.writerows([k,*v0,*(['']*(len(cols)+1))] for k,v0 in [('TLS',t),('VA',v),('OUT',x)])
