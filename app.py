"""GVC Explorer — local, interactive WWZ T1–T16 analysis dashboard.

Run: pip install -e . && streamlit run app.py
No network calls: data remain on the local computer.
"""
from __future__ import annotations
import io
import tempfile
import zipfile
from pathlib import Path
import json
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from gvc import load_2007_global, load_reference_terms, compute_wwz, reference_comparison
from gvc.engine import IOSystem, WWZResult
from gvc.studio_io import catalog as studio_catalog, digest
from gvc.terms import TERMS as TERM_INFO
from gvc.metadata import load_oecd_icio_catalog, resolve_labels, OECD_ICIO_SCHEMA, oecd_metadata_template

ROOT=Path(__file__).resolve().parent
REFERENCE=ROOT/'data'/'reference_2007'
TERMS=[f'T{i}' for i in range(1,17)]
GROUPS=(['T1: 直接最终产品'] + [f'T{k}: 中间投入路径' for k in range(2,10)] +
        ['T10: 出口重复核算'] + [f'T{k}: 直接进口方来源' for k in range(11,14)] +
        [f'T{k}: 第三方来源' for k in range(14,17)])
CODE_GROUP=['直接最终产品']+['本国增加值（中间投入路径）']*8+['本国重复核算']+['进口方来源']*3+['其他经济体来源']*3
COLORS={'直接最终产品':'#194568','本国增加值（中间投入路径）':'#467d9a','本国重复核算':'#8b9d9f','进口方来源':'#c58a47','其他经济体来源':'#916657'}

st.set_page_config(page_title='GVC Explorer | WWZ 16',page_icon='🌐',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
:root,.stApp{color-scheme:only light}
.stApp,[data-testid="stAppViewContainer"]{background:#f5f6f7;color:#202328}
.block-container{padding-top:2.5rem;max-width:1400px}
[data-testid="stHeader"],[data-testid="stSidebar"]{background:#fff}
[data-testid="stSidebar"]{border-right:1px solid #dadde1}
[data-testid="stMetric"]{border:1px solid #dadde1;border-radius:6px;padding:10px 14px;background:#fff;color:#202328;font-variant-numeric:tabular-nums}
h1,h2,h3{letter-spacing:-.035em;color:#202328}
.stApp a{color:#1e48ad;text-underline-offset:3px}
.gvc-tag{display:inline-flex;align-items:center;gap:7px;color:#555d67;font:500 13px/1.4 system-ui,sans-serif}
.gvc-tag::before{content:"";width:8px;height:8px;background:#bfde3c;border:1px solid #718820;border-radius:50%}
.stApp :is(button,input,summary):focus-visible{outline:2px solid #2454cf;outline-offset:2px}
</style>''',unsafe_allow_html=True)


def show_chart(fig):
    fig.update_layout(template='plotly_white',paper_bgcolor='#ffffff',plot_bgcolor='#ffffff',
                      font_color='#202328',hoverlabel={'bgcolor':'#ffffff','font_color':'#202328'})
    fig.update_xaxes(gridcolor='#e5e7ea',zerolinecolor='#a2a8b1')
    fig.update_yaxes(gridcolor='#e5e7ea',zerolinecolor='#a2a8b1')
    st.plotly_chart(fig,use_container_width=True,theme=None)



def load_directory(folder:Path,s:int,n:int)->tuple[WWZResult,dict]:
    assert folder.is_dir(),f'Not a directory: {folder}'
    io_xlsx=folder/'2007global.xlsx'
    if io_xlsx.is_file():
        io_data=load_2007_global(io_xlsx,s,n)
    elif all((folder/f'{fn}.csv').is_file() for fn in ('Z','Y','VA','X')):
        def read(name):return np.loadtxt(folder/f'{name}.csv',delimiter=',')
        io_data=IOSystem(read('Z'),read('Y'),read('VA').reshape(-1),read('X').reshape(-1),s,n).validate()
    else:
        raise ValueError('No recognized input: provide 2007global.xlsx (Sheet2), or Z.csv, Y.csv, VA.csv, X.csv')
    meta={'source':str(folder),'input_format':'legacy 2007global.xlsx / Sheet2' if io_xlsx.is_file() else 'canonical CSV','countries':s,'sectors':n}
    if (folder/'metadata.json').is_file():
        with (folder/'metadata.json').open(encoding='utf-8') as f:
            user_meta=json.load(f)
        for key in ('year','unit','country_names','industry_names','classification','axis_order_confirmed','economy_codes','sector_codes'):
            if key in user_meta:meta[key]=user_meta[key]
    if io_xlsx.is_file():
        ref = studio_catalog('legacy_axes')
        if digest(io_xlsx) == ref['sha256'] and (s,n)==(48,17):
            meta.update(year=2007, unit='USD million', country_names=[i['zh']+' / '+i['en'] for i in ref['areas']], industry_names=[i['zh']+' / '+i['en'] for i in ref['sectors']])
    # Validate label provenance before the expensive WWZ computation.
    _, _, meta['label_source'] = resolve_labels(meta, s, n)
    result=compute_wwz(io_data)
    if all((folder/f'T{k}va2007.csv').is_file() for k in range(1,17)):
        meta['matlab_parity']=reference_comparison(result,folder)
    return result,meta


@st.cache_resource(show_spinner='正在计算 16 项分解…')
def cached_directory(path_str:str,s:int,n:int,stamp:str):
    return load_directory(Path(path_str),s,n)


def read_bundle(uploaded,s,n):
    with tempfile.TemporaryDirectory(prefix='gvc_') as tmp:
        root=Path(tmp)
        with zipfile.ZipFile(io.BytesIO(uploaded)) as z:
            for item in z.infolist():
                target=(root/item.filename).resolve()
                if not target.is_relative_to(root.resolve()):
                    raise ValueError('Unsafe path in ZIP archive')
                if item.is_dir():continue
                if item.file_size>1_000_000_000:raise ValueError('ZIP member exceeds 1GB safety limit')
                target.parent.mkdir(parents=True,exist_ok=True)
                with z.open(item) as source,target.open('wb') as dest:
                    import shutil;shutil.copyfileobj(source,dest)
        matches=sorted(list(root.rglob('2007global.xlsx')) + [p.parent for p in root.rglob('Z.csv')])
        for m in matches:
            folder=m.parent if m.is_file() else m
            try:
                result,meta=load_directory(folder,s,n)
                meta['source']=uploaded.name
                return result,meta
            except (FileNotFoundError,ValueError,AssertionError):
                continue
        raise ValueError('ZIP has no matching complete IO dataset')


def dataframe_from_result(result, exporter,importer,sector):
    idx=exporter*result.sectors+sector
    vals=result.terms[:,idx,importer]
    total=result.total_exports[idx,importer]
    return pd.DataFrame({'term':TERMS,'group':CODE_GROUP,'value':vals,
                        'share_of_gross_exports_pct':100*vals/total if total !=0 else np.full(16,np.nan)}),total


def export_fig(df, title, fmt):
    from gvc.publication import bar_figure
    buf=io.BytesIO()
    fig=bar_figure(df,title)
    fig.savefig(buf,format=fmt,dpi=300,bbox_inches='tight')
    import matplotlib.pyplot as plt
    plt.close(fig)
    return buf.getvalue()


st.markdown('<span class="gvc-tag" lang="en">For research only</span>',unsafe_allow_html=True)
st.title('GVC Explorer')
st.markdown('Global Value Chain Decomposition · WWZ 16-term accounting · Local research tool  \n本软件由 [Jiacheng Zheng](https://karcen.github.io/) 使用 Codex 辅助开发。')
with st.sidebar:
    st.header('数据源 / Data source')
    choice=st.radio('输入方式',('内置 2007 样例','本地 IO 文件夹','上传 ZIP 数据包'),index=0)
    s=st.number_input('经济体/地区数量',min_value=2,max_value=200,value=48,step=1)
    n=st.number_input('每个经济体的产业数',min_value=1,max_value=200,value=17,step=1)
    folder=st.text_input('本地路径',value=str(REFERENCE)) if choice=='本地 IO 文件夹' else None
    archive=st.file_uploader('IO 数据 ZIP',type=['zip']) if choice=='上传 ZIP 数据包' else None
    run=st.button('载入并计算',type='primary',use_container_width=True)
    st.divider()
    st.caption('仅本地计算；不会自动上传原始 IO 数据。')
    st.markdown('Project by [Jiacheng Zheng](https://karcen.github.io/)')

if run:
    try:
        if choice=='内置 2007 样例':
            p=REFERENCE;stamp=str((p/'2007global.xlsx').stat().st_mtime_ns)
            output=cached_directory(str(p),int(s),int(n),stamp)
        elif choice=='本地 IO 文件夹':
            p=Path(folder).expanduser();assert p.is_dir(),f'Folder not found: {p}'
            files=[x for x in p.iterdir() if x.is_file()]
            stamp=str([(x.name,x.stat().st_size,x.stat().st_mtime_ns) for x in files])
            output=cached_directory(str(p),int(s),int(n),stamp)
        else:
            assert archive is not None,'Please select a ZIP file'
            output=read_bundle(archive.getvalue(),int(s),int(n))
        st.session_state['output']=output
    except Exception as exc:
        st.error(f'输入或计算失败: {type(exc).__name__}: {exc}')


page=st.radio('页面',('16 项分解','国家与产业','双边出口比较','数值验证与导出','OECD ICIO 2025 代码表'),horizontal=True)

if page=='OECD ICIO 2025 代码表':
    catalog=load_oecd_icio_catalog()
    st.subheader('OECD ICIO 2025 Extended · Official economy / industry labels')
    st.caption('来源：ReadMe_ICIO_extended.xlsx · Area_Activities / RowItems / ColItems。'
               '85 个代码包含 80 个经济体、ROW 及中国和墨西哥的 4 个拆分项。'
               '与 2007 年 MATLAB 样例的 48×17 排列不同，不能按位置套用。')
    a,b=st.columns(2)
    with a:
        st.metric('Economy / area codes',len(catalog['economies']))
        q_e=st.text_input('搜索经济体名称或代码',placeholder='CHN, Germany, Mexico ...')
        economies=pd.DataFrame(catalog['economies'])
        if q_e:
            economies=economies[economies['code'].str.contains(q_e,case=False,regex=False)|economies['name'].str.contains(q_e,case=False,regex=False)]
        st.dataframe(economies,hide_index=True,use_container_width=True,height=490)
    with b:
        st.metric('ISIC Rev.4 industry groups',len(catalog['sectors']))
        q_s=st.text_input('搜索行业名称、代码或 ISIC 分类',placeholder='C26, financial, 64 ...')
        industries=pd.DataFrame(catalog['sectors'])
        if q_s:
            industries=industries[industries['code'].str.contains(q_s,case=False,regex=False)|industries['name'].str.contains(q_s,case=False,regex=False)|industries['isic_rev4'].str.contains(q_s,case=False,regex=False)]
        st.dataframe(industries,hide_index=True,use_container_width=True,height=490)
    st.caption('OECD (2025). OECD Inter-Country Input-Output Database. https://oe.cd/icio · Nominal values: million current USD. '
               'RowItems / ColItems first 4,250 entries: 85 economies × 50 activities; verify input matrix order independently.')
    st.download_button('下载经济体与产业代码 JSON',json.dumps(catalog,ensure_ascii=False,indent=2).encode('utf-8'),
                       file_name='oecd_icio_2025_extended.json',mime='application/json')
    st.download_button('下载经济体代码 CSV',pd.DataFrame(catalog['economies']).to_csv(index=False).encode('utf-8-sig'),
                       file_name='oecd_icio_2025_economies.csv',mime='text/csv')
    st.download_button('下载产业代码 CSV',pd.DataFrame(catalog['sectors']).to_csv(index=False).encode('utf-8-sig'),
                       file_name='oecd_icio_2025_sectors.csv',mime='text/csv')
    st.divider()
    st.markdown('#### 将 OECD 名称应用于新 IO 数据')
    st.info('下载 metadata.json 模板，核对 Z / Y / VA / X 的经济体和产业顺序。只有顺序与 OECD README 完全一致后，'
            '才能把 axis_order_confirmed 改为 true。将模板保存为数据文件夹内的 metadata.json。'
            '内置 2007 年 48×17 样例不可使用该模板。')
    st.download_button('下载 OECD 元数据模板',json.dumps(oecd_metadata_template(),ensure_ascii=False,indent=2).encode('utf-8'),
                       file_name='metadata.json',mime='application/json')
    st.stop()

if 'output' not in st.session_state:
    st.info('选择数据源后点击“载入并计算”。默认内置完整 2007 年 48×17 案例。')
    st.stop()

result,meta=st.session_state['output']
S,N=result.countries,result.sectors
names,industries,label_source=resolve_labels(meta,S,N)
assert len(names)==S and len(industries)==N,'Country/industry labels have incorrect length'
err=np.abs(result.discrepancy).max()
with st.container():
    c1,c2,c3,c4=st.columns(4)
    c1.metric('经济体 / 地区',S)
    c2.metric('产业',N)
    c3.metric('总出口额（当前数据）',f'{result.total_exports.sum():,.2f}')
    c4.metric('最大恒等式残差',f'{err:.2e}')
st.caption(f'经济体／产业标签来源：{label_source}。OECD ICIO 2025 的真实名称仅能用于轴顺序已确认的 85×50 数据；请使用「OECD ICIO 2025 代码表」浏览官方名称。')

if page=='16 项分解':
    a,b,c=st.columns(3)
    with a:ex=st.selectbox('出口经济体 / Exporter',list(range(S)),format_func=lambda i:names[i])
    with b:im=st.selectbox('进口经济体 / Importer',[i for i in range(S) if i!=ex],format_func=lambda i:names[i])
    with c:sec=st.selectbox('产业 / Industry',list(range(N)),format_func=lambda i:industries[i])
    df,total=dataframe_from_result(result,ex,im,sec)
    c1,c2=st.columns(2)
    c1.metric('该产业双边总出口额',f'{total:,.4f}')
    c2.metric('16 项合计',f'{df.value.sum():,.4f}')
    fig=px.bar(df,x='value',y='term',orientation='h',color='group',color_discrete_map=COLORS,
        custom_data=['share_of_gross_exports_pct','group'])
    fig.update_traces(hovertemplate='%{y}<br>Value: %{x:,.6f}<br>Gross export share: %{customdata[0]:.3f}%<br>%{customdata[1]}<extra></extra>')
    fig.update_layout(title=f'{names[ex]} → {names[im]} · {industries[sec]} · 16 Terms',height=600,
        xaxis_title=f'Amount ({meta.get("unit","unit not supplied")})',yaxis_title='',yaxis={'categoryorder':'array','categoryarray':TERMS[::-1]},
        legend_title_text='Code grouping',margin={'l':20,'r':20,'b':40,'t':70})
    show_chart(fig)
    st.dataframe(df,hide_index=True,use_container_width=True)
    chosen_term=st.selectbox('查看分解项公式及来源',list(range(16)),format_func=lambda k:f'{TERM_INFO[k].key} — {TERM_INFO[k].label_zh}')
    info=TERM_INFO[chosen_term]
    st.caption(f'源文件 valueadded2007.m 第 {info.source_lines} 行 · {info.formula}。标签根据源码结构简述，不等于正式文献名称。')
    st.download_button('下载当前筛选 CSV',df.to_csv(index=False).encode('utf-8-sig'),file_name='WWZ_16_selected.csv',mime='text/csv')
    fmt=st.selectbox('科研图输出',('svg','pdf','png'))
    st.download_button(f'下载科研图 ({fmt.upper()})',export_fig(df,f'{names[ex]} to {names[im]} — {industries[sec]}',fmt),file_name=f'WWZ_16_{ex+1}_{im+1}_{sec+1}.{fmt}')

elif page=='国家与产业':
    dest=st.selectbox('分析对象：出口经济体',list(range(S)),format_func=lambda i:names[i])
    view=st.selectbox('指标',('Gross exports',)+tuple(TERMS))
    if view=='Gross exports':
        matrix=result.total_exports.reshape(S,N,S)[dest,:,:]
    else:
        matrix=result.terms[int(view[1:])-1].reshape(S,N,S)[dest,:,:]
    fig=px.imshow(matrix,x=[x.split(' — ',1)[0] for x in names],y=[x.split(' — ',1)[0] for x in industries],color_continuous_scale='Blues',aspect='auto',labels={'x':'进口经济体','y':'产业','color':'金额'})
    fig.update_layout(title=f'{names[dest]} · 产业 × 贸易伙伴热力图',height=max(400,N*27))
    show_chart(fig)
    groups=pd.DataFrame({'importer':names,'gross_exports':matrix.sum(axis=0)})
    st.dataframe(groups,hide_index=True,use_container_width=True)

elif page=='双边出口比较':
    pick=st.multiselect('选择出口经济体（可多选）',list(range(S)),default=list(range(min(4,S))),format_func=lambda i:names[i])
    chosen=st.selectbox('目标进口经济体',list(range(S)),format_func=lambda i:names[i])
    if pick:
        rows=[]
        for origin in pick:
            if origin==chosen:continue
            for t in range(16):
                val=result.terms[t].reshape(S,N,S)[origin,:,chosen].sum()
                rows.append({'Exporter':names[origin],'term':TERMS[t],'Amount':val})
        df=pd.DataFrame(rows)
        if not df.empty:
            fig=px.bar(df,x='Exporter',y='Amount',color='term',barmode='relative',title='WWZ 16 项：出口方比较（产业求和）')
            show_chart(fig)
            st.download_button('下载比较数据',df.to_csv(index=False).encode('utf-8-sig'),file_name='WWZ_comparison.csv',mime='text/csv')
        else:st.info('选择至少一个不同于进口经济体的出口经济体。')

else:
    st.subheader('计算质量与方法验证')
    st.write({'input':meta['source'],'countries':S,'sectors':N,'year':meta.get('year','2007 (legacy filename only)'),
              'unit':meta.get('unit','not established'),'max_abs_export_identity_error':float(err),
              'sum_of_export_identity_errors':float(result.discrepancy.sum())})
    if 'matlab_parity' in meta:
        parity=pd.DataFrame.from_dict(meta['matlab_parity'],orient='index')
        st.dataframe(parity,use_container_width=True)
        st.caption('与既有 MATLAB 导出 CSV 比较；CSV 约有 5–6 位有效数字，比较误差包含 CSV 舍入误差。')
    else:st.warning('该数据源没有原始 T1–T16 CSV，对照测试未执行。')
    data=io.BytesIO()
    np.savez_compressed(data,terms=result.terms,total_exports=result.total_exports,discrepancy=result.discrepancy)
    st.download_button('下载完整核算结果 NPZ',data.getvalue(),file_name='wwz_decomposition.npz',mime='application/octet-stream')
    records=[]
    for exporter in range(S):
        for sec in range(N):
            for importer in range(S):
                if exporter==importer:continue
                idx=exporter*N+sec
                row={'exporter_index':exporter+1,'importer_index':importer+1,'sector_index':sec+1,
                     'gross_exports':result.total_exports[idx,importer]}
                row.update({f'T{t+1}':result.terms[t,idx,importer] for t in range(16)})
                records.append(row)
    long=pd.DataFrame.from_records(records)
    st.download_button('下载完整双边产业结果 CSV',long.to_csv(index=False).encode('utf-8-sig'),file_name='wwz_all_exporter_sector_importer.csv',mime='text/csv')

st.caption('Method: Wang, Z., Wei, S. J., & Zhu, K. (2013). Quantifying international production sharing at the bilateral and sector levels (No. w19677). National Bureau of Economic Research. · [Jiacheng Zheng](https://karcen.github.io/)')
st.caption('The regional-link program has not been ported. OECD ICIO 2025 labels require confirmed dataset dimensions and axis order.')
