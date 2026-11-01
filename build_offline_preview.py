"""Build a self-contained interactive HTML viewer from verified 2007 results."""
from pathlib import Path
import numpy as np
import json
from plotly.offline import get_plotlyjs
from gvc.metadata import load_oecd_icio_catalog
root=Path(__file__).resolve().parent
r=np.load(root/'output/wwz_python_2007.npz')
terms=json.dumps(r['terms'].tolist(),separators=(',',':'))
gross=json.dumps(r['total_exports'].tolist(),separators=(',',':'))
catalog=json.dumps(load_oecd_icio_catalog(),ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
html='''<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>GVC Explorer · 2007</title>
<script>
(function(){
  const systemDark=window.matchMedia('(prefers-color-scheme: dark)').matches;
  let choice=null;
  try { choice=localStorage.getItem('gvc-explorer-theme'); } catch(e) { /* file: storage can be restricted */ }
  document.documentElement.dataset.theme = choice==='light'||choice==='dark'?choice:(systemDark?'dark':'light');
})();
</script>
<style>
:root{color-scheme:light;--page:#f3f6f8;--card:#fff;--panel:#f6f9fa;--header:#12364d;--ink:#233d4f;--ink-strong:#12364d;--muted:#627787;--border:#d9e3e8;--control-border:#b6c8d3;--accent:#215f88;--header-sub:#c9d7e0;--header-link:#b9e6f1;--warn-bg:#fff8ec;--warn-text:#594120;--focus:#398ac9}
html[data-theme="dark"]{color-scheme:dark;--page:#0e1722;--card:#172536;--panel:#1d3042;--header:#0b1a29;--ink:#e2ebf3;--ink-strong:#f1f6fb;--muted:#afc2d2;--border:#31475c;--control-border:#456078;--accent:#72bce8;--header-sub:#b5ccdc;--header-link:#a3d9fc;--warn-bg:#30291e;--warn-text:#eed29c;--focus:#82c3f0}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font:15px/1.55 Arial,'PingFang SC',sans-serif;transition:background .2s,color .2s}
header{background:var(--header);color:#f6fbff;padding:25px max(28px,calc((100% - 1240px)/2))}
header a{color:var(--header-link);text-decoration:underline;text-underline-offset:3px}
header .identity{margin-top:10px;font-size:13px;color:var(--header-sub)}
header h1{font-size:28px;margin:0}
header p{margin:0;color:var(--header-sub)}
.header-top{display:flex;justify-content:space-between;align-items:flex-start;gap:15px}
.theme-toggle{background:transparent;border:1px solid #6d93ac;border-radius:7px;color:#ecf6fc;padding:8px 13px;white-space:nowrap;font:inherit;font-size:13px;cursor:pointer}
.theme-toggle:hover{background:#284257}
button:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid var(--focus);outline-offset:3px}
main{max-width:1280px;margin:auto;padding:20px}
section{background:var(--card);border:1px solid var(--border);border-radius:9px;padding:15px 20px;margin:15px 0}
.controls{display:flex;gap:15px;flex-wrap:wrap}
.controls label{flex:1;min-width:180px;font-size:12px;color:var(--muted);font-weight:bold}
select,input[type=search]{display:block;width:100%;padding:10px;margin-top:5px;border-radius:5px;border:1px solid var(--control-border);color:var(--ink);font:inherit;background:var(--card)}
.kpi{display:grid;grid-template-columns:repeat(4,1fr);gap:15px}
.kpi article{background:var(--card);border:1px solid var(--border);padding:16px;border-radius:8px}
.kpi strong{display:block;font-size:23px;color:var(--ink-strong)}
.kpi small{color:var(--muted)}
.split{display:grid;grid-template-columns:1.2fr 1fr;gap:15px}
.catalog-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.catalog-grid .entry{padding:16px;background:var(--panel);border:1px solid var(--border);border-radius:6px;min-height:130px;margin-top:10px}
.catalog-grid .entry strong{display:block;font-size:17px;margin-bottom:8px}
.catalog-grid .entry small{color:var(--muted)}
.alert{border-left:4px solid #d49856;padding:12px 15px;background:var(--warn-bg);color:var(--warn-text);font-size:13px}
.split section{margin-top:0}
h2{font-size:18px;margin:3px 0 0}
p.note{font-size:13px;color:var(--muted)}
main a{color:var(--accent)}
@media(max-width:850px){.kpi{grid-template-columns:1fr 1fr}.split,.catalog-grid{grid-template-columns:1fr}}
@media(max-width:520px){.header-top{align-items:stretch;flex-direction:column}.theme-toggle{align-self:flex-start}.kpi{grid-template-columns:1fr 1fr}}
@media(prefers-reduced-motion:reduce){body{transition:none}}
</style></head><body>
<header><div class="header-top"><div><h1>GVC Explorer</h1><p>Global value chain · 16-term WWZ decomposition · 2007 offline analysis</p></div><button id="theme-toggle" class="theme-toggle" type="button" aria-label="Switch to dark mode" aria-pressed="false">◐ Dark mode</button></div><div class="identity">Developed by <a href="https://karcen.github.io/" target="_blank" rel="noopener noreferrer">Jiacheng Zheng</a></div></header>
<main><section class="controls"><label>Exporter / 出口经济体<select id="ex"></select></label><label>Importer / 进口经济体<select id="im"></select></label><label>Industry / 产业<select id="sec"></select></label><label>Heatmap measure / 指标<select id="term"></select></label></section>
<div class="kpi"><article><strong id="gross"></strong><small>Gross bilateral exports</small></article><article><strong id="total"></strong><small>Sum of 16 terms</small></article><article><strong id="residual"></strong><small>Export identity residual</small></article><article><strong>48 × 17</strong><small>Economies × industries</small></article></div>
<section><h2>16-term decomposition</h2><p class="note">Signed values; hover to inspect contribution and denominator.</p><div id="bars" style="height:590px"></div></section>
<div class="split"><section><h2>Industry × destination</h2><p class="note">Click a heatmap cell to change the selected pair.</p><div id="heat" style="height:580px"></div></section><section><h2>Destination concentration</h2><p class="note">Highest 15 destinations, summing over industries.</p><div id="rank" style="height:580px"></div></section></div>
<section id="oecd-catalog"><h2>OECD ICIO 2025 Extended · Economy &amp; industry directory</h2><p class="note">Verified from the OECD README (2025 edition), <i>Area_Activities</i>, <i>RowItems</i> and <i>ColItems</i>. View the real codes and descriptions independently of the legacy 2007 calculations.</p><div class="alert"><b>Different data structures:</b> OECD ICIO 2025 Extended defines 85 area codes × 50 industries, including split Mexico and split China. The MATLAB results above contain 48 economy indices × 17 sectors. It would be incorrect to assign the 2025 labels to those 2007 series by position.</div><div class="catalog-grid"><div><label>OECD economy / area<select id="catalogEconomy"></select></label><div class="entry" id="catalogEconomyDetail"></div></div><div><label>OECD industry / activity<select id="catalogSector"></select></label><div class="entry" id="catalogSectorDetail"></div></div></div><p class="note">Source: OECD (2025), Inter-Country Input-Output Database (<a href="https://oe.cd/icio" target="_blank" rel="noopener noreferrer">OECD ICIO</a>); values in current USD million. The four split entries are not four additional sovereign states.</p></section>
<p class="note">Method: Wang, Z., Wei, S. J., &amp; Zhu, K. (2013). <i>Quantifying international production sharing at the bilateral and sector levels</i> (No. w19677). National Bureau of Economic Research. <a href="https://www.nber.org/papers/w19677" target="_blank" rel="noopener noreferrer">NBER Working Paper</a>.</p>
<p class="note">The original 2007 workbook has no verified economy/industry label mapping. Economy and Sector index numbers above are not country names. This offline file explores previously computed results; new IO inputs require the Python GUI. No external network access is needed for the visualization. · <a href="https://karcen.github.io/" target="_blank" rel="noopener noreferrer">Jiacheng Zheng</a></p></main>
<script>__PLOTLY__</script><script>const T=__TERMS__;const G=__GROSS__;const OECD=__OECD_CATALOG__;
const $=id=>document.getElementById(id);const fmt=x=>Number(x).toLocaleString('en-US',{maximumFractionDigits:4});
const THEME_KEY='gvc-explorer-theme';
const isDark=()=>document.documentElement.dataset.theme==='dark';
const themeButton=$('theme-toggle');
function refreshThemeControl(){const dark=isDark();themeButton.textContent=dark?'☀ Light mode':'◐ Dark mode';themeButton.setAttribute('aria-label',dark?'Switch to light mode':'Switch to dark mode');themeButton.setAttribute('aria-pressed',String(dark));}
function toggleTheme(){document.documentElement.dataset.theme=isDark()?'light':'dark';try{localStorage.setItem(THEME_KEY,document.documentElement.dataset.theme);}catch(e){/* file: storage can be restricted */}refreshThemeControl();render();}
themeButton.addEventListener('click',toggleTheme);refreshThemeControl();
const colors=['#194568',...Array(8).fill('#467d9a'),'#8499a4',...Array(3).fill('#c58a47'),...Array(3).fill('#916657')];
const group=['Direct final exports',...Array(8).fill('Intermediate-input pathway'),'Domestic double counting',...Array(3).fill('Direct importer source'),...Array(3).fill('Other foreign sources')];
for(let i=0;i<48;i++){let a=new Option('Economy '+String(i+1).padStart(2,'0'),i);$('ex').add(a);$('im').add(a.cloneNode(true))}
for(let i=0;i<17;i++)$('sec').add(new Option('Sector '+String(i+1).padStart(2,'0'),i));
$('term').add(new Option('Gross exports','gross'));for(let i=0;i<16;i++)$('term').add(new Option('T'+(i+1),i));
$('im').value='1';
for(const economy of OECD.economies){$('catalogEconomy').add(new Option(economy.code+' — '+economy.name,economy.code))}
for(const sector of OECD.sectors){$('catalogSector').add(new Option(sector.code+' — '+sector.name,sector.code))}
$('catalogEconomy').value='CHN';$('catalogSector').value='C26';
function renderCatalog(){
  const e=OECD.economies.find(x=>x.code===$('catalogEconomy').value);
  const i=OECD.sectors.find(x=>x.code===$('catalogSector').value);
  $('catalogEconomyDetail').textContent='';
  const a=document.createElement('strong');a.textContent=e.code+' — '+e.name;
  const b=document.createElement('small');b.textContent='OECD 2025 Area_Activities position '+e.position+' / 85';
  $('catalogEconomyDetail').append(a,b);
  $('catalogSectorDetail').textContent='';
  const c=document.createElement('strong');c.textContent=i.code+' — '+i.name;
  const d=document.createElement('small');d.textContent='ISIC Rev.4: '+i.isic_rev4+' · position '+i.position+' / 50';
  $('catalogSectorDetail').append(c,d);
}
for(const id of ['catalogEconomy','catalogSector'])$(id).addEventListener('change',renderCatalog);
renderCatalog();
function plotLayout(){let dark=isDark();return {template:dark?'plotly_dark':'plotly_white',paper_bgcolor:dark?'#172536':'#fff',plot_bgcolor:dark?'#172536':'#fff',font:{family:'Arial',size:12,color:dark?'#dae8f2':'#4b6675'},showlegend:false,margin:{l:62,r:25,t:20,b:55}};}
function render(){const layout=plotLayout();const heatScale=isDark()?[[0,'#1c3043'],[0.18,'#254c69'],[0.42,'#326d94'],[0.7,'#5b9fc0'],[1,'#b9e6f2']]:'Blues';let ex=+$('ex').value,im=+$('im').value,sec=+$('sec').value,term=$('term').value;
if(ex===im){$('im').value=(ex+1)%48;return render()}
let idx=ex*17+sec,vals=Array.from({length:16},(_,i)=>T[i][idx][im]),g=G[idx][im],sum=vals.reduce((a,b)=>a+b,0);
$('gross').textContent=fmt(g);$('total').textContent=fmt(sum);$('residual').textContent=Math.abs(g-sum).toExponential(2);
Plotly.react('bars',[{type:'bar',orientation:'h',x:vals,y:Array.from({length:16},(_,i)=>'T'+(i+1)),marker:{color:colors},customdata:vals.map((v,i)=>`${group[i]}<br>Share of gross exports: ${g?100*v/g:NaN}%`),hovertemplate:'%{y}: %{x:,.6f}<br>%{customdata}<extra></extra>'}],{...layout,yaxis:{autorange:'reversed'},xaxis:{title:'Value (source unit)',zeroline:true,zerolinecolor:isDark()?'#89a8bb':'#586c78'}},{responsive:true,displaylogo:false});
let get=(s,j)=>term==='gross'?G[ex*17+s][j]:T[+term][ex*17+s][j];
let mat=Array.from({length:17},(_,s)=>Array.from({length:48},(_,j)=>get(s,j)));
Plotly.react('heat',[{type:'heatmap',z:mat,x:Array.from({length:48},(_,j)=>j+1),y:Array.from({length:17},(_,j)=>j+1),colorscale:heatScale,hovertemplate:'Sector %{y}; Destination %{x}<br>Value: %{z:,.6f}<extra></extra>'}],{...layout,margin:{l:50,r:20,t:15,b:60},xaxis:{title:'Destination index'},yaxis:{title:'Sector index'}},{responsive:true,displaylogo:false}).then(()=>{const gd=$('heat');if(!gd._gvcBound){gd.on('plotly_click',e=>{const pt=e.points[0];$('im').value=+pt.x-1;$('sec').value=+pt.y-1;render()});gd._gvcBound=true}});
let score=Array.from({length:48},(_,j)=>mat.reduce((v,row)=>v+row[j],0));let top=Array.from({length:48},(_,j)=>j).filter(j=>j!==ex).sort((a,b)=>score[b]-score[a]).slice(0,15).reverse();
Plotly.react('rank',[{type:'bar',orientation:'h',x:top.map(j=>score[j]),y:top.map(j=>'Economy '+(j+1)),marker:{color:isDark()?'#6eb3da':'#467d9a'}}],{...layout,margin:{l:95,r:18,t:15,b:65},xaxis:{title:'Aggregated value'}},{responsive:true,displaylogo:false});
}
for(const id of ['ex','im','sec','term'])$(id).addEventListener('change',render);
render();</script></body></html>'''
html=html.replace('__PLOTLY__',get_plotlyjs()).replace('__TERMS__',terms).replace('__GROSS__',gross).replace('__OECD_CATALOG__',catalog)
p=root/'offline_dashboard.html';p.write_text(html,encoding='utf-8');print(p,p.stat().st_size)
