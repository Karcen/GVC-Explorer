from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from gvc.studio_run import result_at,save_html
from gvc.studio_io import catalog
from gvc.atlas import default_view
if __name__=='__main__':
    m=catalog('legacy_axes');r=result_at(ROOT/'output/wwz_python_2007.npz',m);save_html(ROOT/'offline_dashboard.html',r,m,default_view(r,m))
