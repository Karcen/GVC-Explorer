"""Publication figures and their exact plotted values from the signed WWZ result cube."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import textwrap, csv, json
import numpy as np
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap,TwoSlopeNorm,Normalize
from matplotlib.ticker import MaxNLocator,ScalarFormatter
from .engine import WWZResult
from .pdf_fonts import pdf_faces
from .vendor.nature_figure.audit_pdf_text import audit_pdf

TITLE=[('双边出口的十六项分解','Sixteen components of bilateral exports'),('增加值与重复计算','Value added and double counting'),('出口目的地','Export destinations'),('双边出口的行业构成','Industries in the selected trade flow'),('行业与目的地','Industries by destination'),('双向贸易','Trade in both directions'),('各经济体的进出口','Exports and imports by economy'),('主要双边出口流向','Largest bilateral export flows')]
IDS=['terms','groups','destinations','industries','heatmap','directions','trade_profile','corridors']
GROUPS=[[0,1,2,3,4],[5,6,7],[8,9],[10,11,13,14],[12,15]]
GN=[('境外吸收的本国增加值','Domestic VA absorbed abroad'),('回流的本国增加值','Returned domestic VA'),('本国重复计算','Domestic double counting'),('外国增加值','Foreign VA'),('外国重复计算','Foreign double counting')]
TC='DVA_FIN DVA_INT DVA_INTrex1 DVA_INTrex2 DVA_INTrex3 RDV_FIN1 RDV_FIN2 RDV_INT DDC_FIN DDC_INT MVA_FIN MVA_INT MDC OVA_FIN OVA_INT ODC'.split()
COL=['#286775','#d58b3b','#8e6b8b','#5583af','#758b59']; INK='#23343e'; SOFT='#667680'

def la(pair,lang):return pair[lang=='en']
def axisnames(m,k,lang):return [r[lang] for r in m[k]]
def unit(m,lang):return la(('百万美元','USD million'),lang) if m['unit']=='USD million' else m['unit']
def shortlabel(t,lang):
    if lang=='zh' and len(t)>19:return '\n'.join(t[i:i+19] for i in range(0,len(t),19))
    return textwrap.fill(t,39,break_long_words=False)
@dataclass(frozen=True)
class View:
    exporter:int; importer:int; sector:int=-1; term:int=0

def default_view(r,m):
    # Start with an observed corridor rather than a tiny arbitrary cell.
    areas=[i['code'] for i in m['areas']]
    if m.get('layout')=='legacy_2007':return View(areas.index('DEU'),areas.index('USA'),-1,0)
    g=r.total_exports.reshape(r.countries,r.sectors,r.countries).sum(1);masks=np.where(np.eye(r.countries,dtype=bool),-np.inf,g);a,b=np.unravel_index(np.argmax(masks),g.shape);return View(int(a),int(b))

def sourceview(r,m,v,lang):
    s,n=r.countries,r.sectors;a,b,k,t=v.exporter,v.importer,v.sector,v.term
    if not(0<=a<s and 0<=b<s and a!=b and -1<=k<n and 0<=t<16):raise ValueError('Invalid selection / 无效筛选')
    ae=axisnames(m,'areas',lang);se=axisnames(m,'sectors',lang);allsec=la(('全部行业','All industries'),lang);sub=se[k] if k>=0 else allsec
    g=r.total_exports.reshape(s,n,s);terms=r.terms.reshape(16,s,n,s);gross=g.sum(1) if k<0 else g[:,k,:];vec=(terms[:,a,:,b].sum(1) if k<0 else terms[:,a,k,b]);total=float(gross[a,b]);pair=f'{ae[a]} → {ae[b]}';unitname=unit(m,lang)
    def order(values,idx,count=10):return sorted(idx,key=lambda j:-values[j])[:count]
    p=order(gross[a],[i for i in range(s) if i!=a]);ind=order(g[a,:,b],range(n));world=la(('全部经济体','All economies'),lang)
    heat_p=order(g[a].sum(0),[i for i in range(s) if i!=a]);heat_k=order(g[a].sum(1),range(n),8);heat=terms[t,a][np.ix_(heat_k,heat_p)];d=[(i,j) for i in range(s) for j in range(s) if i!=j];d=sorted(d,key=lambda x:-gross[x])[:10];
    def chart(i,kind,labels,vals,context,**more):return dict(id=IDS[i],title=la(TITLE[i],lang),kind=kind,labels=labels,values=np.asarray(vals,dtype=float),context=context,unit=unitname,**more)
    scope=pair+'  ·  '+sub;prefix=ae[a]+'  ·  '+sub;both=world+'  ·  '+sub
    return [chart(0,'terms',[f'T{i+1}' for i in range(16)],vec,scope),chart(1,'hbar',[la(g,lang) for g in GN],[vec[idx].sum() for idx in GROUPS],scope,colors=COL),chart(2,'hbar',[ae[i] for i in p],gross[a,p],prefix),chart(3,'hbar',[se[i] for i in ind],g[a,ind,b],pair+'  ·  '+allsec),chart(4,'heat',[se[i] for i in heat_k],heat,ae[a]+f'  ·  T{t+1} / '+TC[t],xlabels=[m['areas'][i]['code'] for i in heat_p],xnames=[ae[i] for i in heat_p]),chart(5,'hbar',[pair,f'{ae[b]} → {ae[a]}'],[gross[a,b],gross[b,a]],sub,colors=[COL[0],COL[1]]),chart(6,'scatter',ae,gross.sum(0),both,x=gross.sum(1),selected=a),chart(7,'hbar',[ae[i]+' → '+ae[j] for i,j in d],[gross[i,j] for i,j in d],both)]

def rows(spec):
    if spec['kind']=='heat':return [(l,c,float(spec['values'][i,j])) for i,l in enumerate(spec['labels']) for j,c in enumerate(spec['xnames'])]
    if spec['kind']=='scatter':return list(zip(spec['labels'],map(float,spec['x']),map(float,spec['values'])))
    return list(zip(spec['labels'],map(float,spec['values'])))

def typeface(lang):
    if lang=='en':return 'DejaVu Sans'
    available={f.name for f in fm.fontManager.ttflist}
    for f in ['Noto Sans CJK SC','PingFang SC','Microsoft YaHei','DengXian','SimHei','Noto Sans CJK JP','WenQuanYi Zen Hei','Arial Unicode MS']:
        if f in available:return f
    raise ValueError('中文图形需要中文字体。请安装 Noto Sans CJK SC，或选择 English。 / Install a CJK font for Chinese exports.')

def figure(spec,meta,lang):
    font=typeface(lang); style={'font.family':font,'font.size':8,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':'#88a0a6','axes.linewidth':.55,'axes.unicode_minus':False}
    with mpl.rc_context(style):
        f=Figure(figsize=(183/25.4,116/25.4),dpi=100,facecolor='white');FigureCanvasAgg(f);ax=f.add_subplot();k=spec['kind']; y=spec['values']; labels=spec['labels'];U=spec['unit'];idx=IDS.index(spec['id']);islong=k in ('hbar','heat');f.subplots_adjust(left=.365 if islong else .13,right=.85 if k=='heat' else .96,top=.77,bottom=.22 if k=='heat' else .19)
        f.text(.055,.948,f'GVC  /  {idx+1:02d}      WWZ 16     •     '+str(meta.get('year') or '—'),size=7,color=COL[0],weight='bold');f.text(.055,.86,spec['title'],size=13,weight='bold');f.text(.055,.795,shortlabel(spec['context'],lang).replace('\n',' '),size=8,color=SOFT,wrap=True)
        ax.spines[['top','right']].set_visible(False);ax.tick_params(length=2.2,width=.5,pad=3);ax.set_axisbelow(True)
        if k=='terms':
            colors=[COL[next(j for j,g in enumerate(GROUPS) if i in g)] for i in range(16)];ax.bar(np.arange(16),y,color=colors,width=.73);ax.axhline(0,color=INK,lw=.65);ax.set_xticks(range(16),labels);ax.set_ylabel(U);ax.grid(axis='y',color='#e4e8e7',lw=.5);ax.margins(x=.02)
        elif k=='hbar':
            ax.barh(np.arange(len(y)),y,color=spec.get('colors',COL[0]),height=.55);ax.set_yticks(range(len(y)),[shortlabel(t,lang) for t in labels]);ax.invert_yaxis();ax.set_xlabel(U);ax.axvline(0,lw=.55,color=INK);ax.grid(axis='x',color='#e3e8e6',lw=.5);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
        elif k=='heat':
            # A diverging scale with an explicit zero only when the selection contains both signs.
            lo,hi=float(y.min()),float(y.max());both=lo<0<hi
            cmap=LinearSegmentedColormap.from_list('trade', ['#9d472c','#faf8f0','#286775'] if both else (['#9d472c','#faf8f0'] if hi<=0 and lo<0 else ['#faf8f0','#286775']))
            norm=TwoSlopeNorm(vcenter=0,vmin=-max(-lo,hi),vmax=max(-lo,hi)) if both else Normalize(min(0,lo),max(hi,0) if hi!=lo else max(hi,0)+1)
            im=ax.pcolormesh(np.arange(y.shape[1]+1),np.arange(y.shape[0]+1),y,cmap=cmap,norm=norm,edgecolors='white',linewidth=.3);ax.invert_yaxis();ax.set_yticks(np.arange(len(labels))+.5,[shortlabel(t,lang) for t in labels]);ax.set_xticks(np.arange(len(spec['xlabels']))+.5,spec['xlabels'],rotation=32,ha='right');ax.spines[:].set_visible(False);ax.tick_params(length=0);cb=f.colorbar(im,ax=ax,fraction=.034,pad=.035);cb.set_label(U);cb.outline.set_visible(False)
        elif k=='scatter':
            x=spec['x'];i=spec['selected'];ax.scatter(x,y,s=15,c=COL[0],alpha=.75,linewidths=.4,edgecolors='white');ax.scatter([x[i]],[y[i]],s=48,marker='D',color=COL[1],edgecolors=INK,linewidths=.6,label=labels[i]);ax.legend(fontsize=7,frameon=False,loc='upper left');ax.set_xlabel(la(('出口','Exports'),lang)+' · '+U);ax.set_ylabel(la(('进口','Imports'),lang)+' · '+U);ax.grid(color='#e3e8e6',lw=.5)
        for axis in ([ax.xaxis] if k=='hbar' else [ax.yaxis] if k=='terms' else [ax.xaxis,ax.yaxis] if k=='scatter' else []):
            axis.set_major_locator(MaxNLocator(nbins=5));fmt=ScalarFormatter(useOffset=False);fmt.set_scientific(False);axis.set_major_formatter(fmt)
        foot=la(('教学模拟数据','Synthetic fixture'),lang) if meta.get('fixture') else meta['source'];f.text(.055,.053,(foot[:60]+'  |  '+meta['basis']+'  |  '+U),size=6.6,color=SOFT);return f

def export_atlas(r,m,v,lang,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);nature=[]
    for spec in sourceview(r,m,v,lang):
        fig=figure(spec,m,lang);p=out/spec['id'];
        with mpl.rc_context({'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'gvc-atlas'}):
            with pdf_faces(fig):fig.savefig(p.with_suffix('.pdf'),format='pdf')
            fig.savefig(p.with_suffix('.png'),format='png',dpi=450)
            fig.savefig(p.with_suffix('.svg'),format='svg')
        audit=audit_pdf(p.with_suffix('.pdf').read_bytes(),minimum_pt=6.5)
        if not audit['auditable'] or audit['below_minimum_count']:
            raise ValueError('Nature Figure PDF text audit failed: '+str(p))
        nature.append(dict(pdf=p.with_suffix('.pdf').name,**audit))
        fig.clear()
        with p.with_suffix('.csv').open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.writer(f);w.writerow(['industry','destination','amount'] if spec['kind']=='heat' else ['economy','exports','imports'] if spec['kind']=='scatter' else ['label','amount']);w.writerows(rows(spec))
    (out/'nature_text_audit.json').write_text(json.dumps({'git_blob':'10830f22870fe00f365df3989e0af56e6481cb21','results':nature},indent=2),encoding='utf-8')
    (out/'selection.json').write_text(json.dumps({'view':v.__dict__,'indices':'zero-based; sector -1 = all','language':lang,'source':m['source'],'unit':m['unit'],'basis':m['basis']},indent=2,ensure_ascii=False),encoding='utf-8')
