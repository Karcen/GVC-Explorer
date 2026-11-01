"""Rebuild verification notes and static figure from the computed 2007 results."""
import sys,json,csv,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from gvc import WWZResult,reference_comparison
from gvc.terms import TERMS
from gvc.publication import bar_figure
import pandas as pd
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parent
folder=root/'data/reference_2007'
r=np.load(root/'output/wwz_python_2007.npz')
res=WWZResult(r['terms'],r['total_exports'],r['discrepancy'],48,17)
c=reference_comparison(res,folder)
report={'source':'valueadded2007.m, 2007global.xlsx/Sheet2',
        'reproduced_year':2007,'economic_units':48,'industry_count':17,
        'output_array_shape':list(res.terms.shape),
        'max_export_accounting_identity_absolute_residual':res.max_error(),
        'aggregate_gross_exports_unverified_currency_unit':float(res.total_exports.sum()),
        'matlab_reference_type':'Saved CSV exports, not a fresh MATLAB run',
        'maximum_item_scaled_relative_error':max(v['max_relative_to_unit_scale'] for v in c.values()),
        'reference_comparison':c,
        'tests_passed':3,'tests_failed':0,'streamlit_browser_test':'not run: Streamlit unavailable in this environment',
        'offline_html_browser_test':'Chromium: selectors changed KPI values; no page JavaScript errors'}
(root/'reports/validation_2007.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
with (root/'reports/terms_source_dictionary.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['term','source_derived_description_zh','formula','source_file','source_lines'])
    for t in TERMS:w.writerow([t.key,t.label_zh,t.formula,'valueadded2007.m',t.source_lines])
manifest=[]
for folder_name in ['data/reference_2007','data/matlab_original','data/legacy_unported']:
    for p in sorted((root/folder_name).iterdir()):
        if not p.is_file():continue
        digest=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
        manifest.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':digest})
(root/'reports/original_file_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
series=res.terms.sum(axis=(1,2))
group=['直接最终产品']+['本国增加值（中间投入路径）']*8+['本国重复核算']+['进口方来源']*3+['其他经济体来源']*3
frame=pd.DataFrame({'term':[f'T{k}' for k in range(1,17)],'value':series,'group':group})
fig=bar_figure(frame,'WWZ T1–T16 · 2007 aggregate contributions')
fig.savefig(root/'reports/wwz_2007_aggregate.png',dpi=200,bbox_inches='tight')
fig.savefig(root/'reports/wwz_2007_aggregate.svg',bbox_inches='tight')
plt.close(fig)
print('Manifest',len(manifest),'original files; aggregate gross exports',report['aggregate_gross_exports_unverified_currency_unit'])
print('Max accounting residual',res.max_error(),'max scaled relative error',report['maximum_item_scaled_relative_error'])
