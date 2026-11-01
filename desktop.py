"""Native bilingual research workbench. The worker does not touch the Tk main loop."""
from __future__ import annotations
import json,queue,subprocess,sys,threading,webbrowser,zipfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from gvc.atlas import figure,sourceview,default_view,View,TITLE,TC,export_atlas,IDS
from gvc.studio_run import result_at
from gvc.studio_io import catalog,annual_members

class Workspace:
    def __init__(self,win):
        self.w=win;self.lang='zh';self.meta=catalog('legacy_axes');self.r=result_at(ROOT/'output/wwz_python_2007.npz',self.meta);self.view=default_view(self.r,self.meta);self.chart=0;self.out=None;self.base=ROOT/'runs';self.page=ROOT/'offline_dashboard.html';self.pipe=None;self.events=queue.Queue();self.status=('ready',100);self.canvas=None
        from gvc.atlas import typeface
        try:typeface('zh')
        except ValueError as exc:
            self.lang='en';messagebox.showwarning('GVC Explorer',str(exc),parent=win)
        win.title('GVC Explorer · Trade Atlas');win.geometry('1190x800');win.minsize(820,600);win.configure(bg='#f5f3eb');win.protocol('WM_DELETE_WINDOW',self.close);self.build()
    def tr(self,z,e):return z if self.lang=='zh' else e
    def stage(self,s):return {'ready':self.tr('2007 年基准已载入','2007 benchmark loaded'),'read':self.tr('读取并校验表头','Reading and validating input'),'solve':self.tr('计算 WWZ 分解','Computing WWZ components'),'save':self.tr('保存数值结果','Saving numerical results'),'figures':self.tr('生成 24 个图形文件','Rendering 24 figure files'),'html':self.tr('生成离线交互图谱','Building the offline atlas'),'done':self.tr('已写入结果目录','Results saved'),'error':self.tr('运行失败，未发布结果','Run failed; no results published')}[s]
    def build(self):
        if self.canvas:self.canvas.get_tk_widget().destroy();self.canvas.figure.clear();self.canvas=None
        for x in self.w.winfo_children():x.destroy()
        sty=ttk.Style(self.w);sty.theme_use('clam');sty.configure('TCombobox',padding=5,fieldbackground='#fffef9');sty.configure('TButton',padding=(8,5));sty.configure('Horizontal.TProgressbar',background='#427b70',troughcolor='#d7dfd7');
        rail=tk.Frame(self.w,bg='#173d3d',width=238);rail.pack(side='left',fill='y');rail.pack_propagate(False);self.rail=rail
        def label(parent,text,bg,fg,size=11,bold=False):return tk.Label(parent,text=text,bg=bg,fg=fg,font=('TkDefaultFont',size,'bold' if bold else 'normal'),anchor='w',wraplength=208,justify='left')
        label(rail,'RESEARCH  /  ATLAS', '#173d3d','#dda47c',10,True).pack(fill='x',padx=16,pady=(24,3));label(rail,'GVC Explorer','#173d3d','#fffdee',22,True).pack(fill='x',padx=15);label(rail,self.tr('全球价值链 · WWZ 16 项分解','Global value chains · WWZ 16'),'#173d3d','#c2d6cd').pack(fill='x',padx=16,pady=(1,16));
        self.controls=[]
        def button(z,e,act):
            b=ttk.Button(rail,text=self.tr(z,e),command=act);b.pack(fill='x',padx=14,pady=3);self.controls.append(b)
        button('导入年度表或 ZIP…','Import annual table or ZIP…',self.pick);button('导入标准矩阵文件夹…','Import matrix directory…',self.folder);button('重新核算 2007 基准','Recompute 2007 benchmark',lambda:self.start(ROOT/'data/reference_2007/2007global.xlsx'));button('选择输出位置…','Choose output location…',self.destination);button('打开离线交互图谱 ↗','Open interactive atlas ↗',lambda:webbrowser.open(self.page.as_uri()));button('导出当前筛选的全部图…','Export this selection…',self.export);button('English','中文',self.switch)
        self.stat=label(rail,'','#173d3d','#d9e7dd',10);self.stat.pack(fill='x',padx=16,pady=(15,4));self.prog=ttk.Progressbar(rail,maximum=100);self.prog.pack(fill='x',padx=16);self.setstatus(*self.status)
        for txt,href in [(self.tr('本软件由','Developed by'),False),('Jiacheng Zheng',True),(self.tr('使用 Codex 辅助开发。','with assistance from Codex.'),False)]:
            el=label(rail,txt,'#173d3d','#f1c396' if href else '#cfdfd6',11 if href else 9,href);el.pack(fill='x',padx=16,pady=(9 if txt.startswith(('本','Developed')) else 0,0));
            if href:el.configure(cursor='hand2',takefocus=True,font=('TkDefaultFont',11,'underline'));el.bind('<Button-1>',lambda e:webbrowser.open('https://karcen.github.io/'));el.bind('<Return>',lambda e:webbrowser.open('https://karcen.github.io/'))
        main=tk.Frame(self.w,bg='#f5f3eb');main.pack(fill='both',expand=True,padx=14,pady=12);self.banner=tk.Label(main,text=self.meta['source']+'    /    '+str(self.meta.get('year') or '—')+'    /    '+self.meta['basis'],bg='#f5f3eb',fg='#7d4c31',font=('TkDefaultFont',11,'bold'),anchor='w');self.banner.pack(fill='x');filters=tk.Frame(main,bg='#f5f3eb');filters.pack(fill='x');self.boxes=[]
        pairs=[('出口经济体','Exporter'),('进口经济体','Importer'),('出口行业','Industry'),('图形','Figure'),('热图分解项','Heatmap term')];areas=[r[self.lang]+' · '+r['code'] for r in self.meta['areas']];secs=[self.tr('全部行业','All industries')]+[r[self.lang] for r in self.meta['sectors']];self.bs=[i for i in range(len(areas)) if i!=self.view.exporter]; lists=[areas,[areas[i] for i in self.bs],secs,[self.tr(*t) for t in TITLE],[f'T{i+1} · {t}' for i,t in enumerate(TC)]];idxs=[self.view.exporter,self.bs.index(self.view.importer),self.view.sector+1,self.chart,self.view.term]
        for i,(pair,vals,ix) in enumerate(zip(pairs,lists,idxs)):
            row,col=divmod(i,3);filters.columnconfigure(col,weight=1,uniform='opts');cell=tk.Frame(filters,bg='#f5f3eb');cell.grid(row=row,column=col,sticky='ew',padx=(0,6),pady=4);tk.Label(cell,text=self.tr(*pair),anchor='w',bg='#f5f3eb',fg='#385a54').pack(fill='x');b=ttk.Combobox(cell,values=vals,state='readonly',width=15);b.pack(fill='x');b.current(ix);b.bind('<<ComboboxSelected>>',self.changed);self.boxes.append(b)
        self.chartbox=tk.Frame(main,bg='white');self.chartbox.pack(fill='both',expand=True,pady=(4,0));self.detail=tk.StringVar();tk.Label(main,textvariable=self.detail,anchor='w',bg='#f5f3eb',fg='#37554f',wraplength=900).pack(fill='x');self.plot()
    def changed(self,_):
        a,b,k,c,t=[x.current() for x in self.boxes];b=self.bs[b];
        if a==b:b=self.view.exporter
        self.view=View(a,b,k-1,t);self.chart=c;self.bs=[i for i in range(self.r.countries) if i!=a];self.boxes[1].configure(values=[self.meta['areas'][i][self.lang]+' · '+self.meta['areas'][i]['code'] for i in self.bs]);self.boxes[1].current(self.bs.index(b));self.plot()
    def plot(self):
        if self.canvas:self.canvas.get_tk_widget().destroy();self.canvas.figure.clear()
        spec=sourceview(self.r,self.meta,self.view,self.lang)[self.chart];f=figure(spec,self.meta,self.lang);self.canvas=FigureCanvasTkAgg(f,master=self.chartbox);self.canvas.draw();self.canvas.get_tk_widget().pack(fill='both',expand=True);self.detail.set(self.tr('移动指针查看数值；打开离线图谱可缩放、点选和下载选区。','Hover to inspect values. Open the atlas for zoom, linked selection and CSV export.'))
        def hover(ev):
            if ev.inaxes!=f.axes[0] or ev.xdata is None:return
            kind=spec['kind'];v=spec['values'];labels=spec['labels'];txt=''
            if kind=='scatter':
                for a in f.axes[0].collections:
                    ok,hit=a.contains(ev)
                    if ok:
                        i=spec['selected'] if a==f.axes[0].collections[-1] else int(hit['ind'][0]);txt=f"{labels[i]} · X {spec['x'][i]:,.4f} / M {v[i]:,.4f}";break
            elif kind=='heat':
                import math
                i,j=math.floor(ev.ydata),math.floor(ev.xdata)
                if 0<=i<v.shape[0] and 0<=j<v.shape[1]:txt=f"{labels[i]} → {spec['xnames'][j]}: {v[i,j]:,.5f}"
            else:
                i=round(ev.xdata if kind=='terms' else ev.ydata)
                if 0<=i<len(labels):txt=f'{labels[i]}: {v[i]:,.5f}'
            if txt:self.detail.set(txt+'  '+spec['unit'])
        self.canvas.mpl_connect('motion_notify_event',hover)
    def switch(self):
        from gvc.atlas import typeface
        new='en' if self.lang=='zh' else 'zh'
        try:typeface(new)
        except ValueError as exc:messagebox.showerror('GVC Explorer',str(exc),parent=self.w);return
        self.lang=new;self.build()
    def destination(self):
        p=filedialog.askdirectory(parent=self.w); 
        if p:self.base=Path(p);self.detail.set(str(self.base))
    def folder(self):
        p=filedialog.askdirectory(parent=self.w)
        if p:self.start(Path(p))
    def pick(self):
        p=filedialog.askopenfilename(parent=self.w,filetypes=[('ICIO / IO','*.csv *.CSV *.gz *.zip *.xlsx'),('All','*')]);
        if not p:return
        p=Path(p)
        if p.suffix.lower()!='.zip':self.start(p);return
        try:
            with zipfile.ZipFile(p) as z:options=annual_members(z)
            if not options:raise ValueError('ZIP 中没有年度 CSV / No annual CSV in ZIP')
        except (OSError,zipfile.BadZipFile,ValueError) as e:messagebox.showerror('GVC Explorer',str(e));return
        if len(options)==1:self.start(p,options[0]);return
        dlg=tk.Toplevel(self.w);dlg.title(self.tr('选择年度表','Select annual table'));dlg.transient(self.w);dlg.grab_set();b=ttk.Combobox(dlg,values=options,state='readonly',width=42);b.pack(padx=12,pady=12);b.current(0)
        def go():m=b.get();dlg.destroy();self.start(p,m)
        ttk.Button(dlg,text=self.tr('开始分析','Analyse'),command=go).pack(pady=8)
    def export(self):
        p=filedialog.askdirectory(parent=self.w)
        if not p:return
        from datetime import datetime
        out=Path(p)/('selection-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));out.mkdir();self.w.config(cursor='watch');self.w.update_idletasks()
        try:export_atlas(self.r,self.meta,self.view,self.lang,out);self.detail.set(str(out))
        finally:self.w.config(cursor='')
    def setstatus(self,s,n):self.status=(s,n);self.stat.config(text=self.stage(s));self.prog['value']=n
    def start(self,path,member=None):
        if self.pipe is not None:return
        args=[sys.executable,str(ROOT/'studio_batch.py'),str(path),'--output',str(self.base),'--language',self.lang];args+=['--member',member] if member else [];self.pipe=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',env=dict(__import__('os').environ,PYTHONIOENCODING='utf-8'));proc=self.pipe;self.setstatus('read',1)
        for b in self.controls:b.state(['disabled'])
        def reader():
            for line in proc.stdout:self.events.put(json.loads(line))
            rc=proc.wait();stderr_thread.join();error=''.join(stderr_lines);self.events.put({'exit':rc,'error':error})
        stderr_lines=[]
        stderr_thread=threading.Thread(target=lambda:stderr_lines.extend(proc.stderr),daemon=True);stderr_thread.start()
        threading.Thread(target=reader,daemon=True).start();self.w.after(75,self.poll)
    def poll(self):
        while not self.events.empty():
            ev=self.events.get_nowait()
            if 'stage' in ev:self.setstatus(ev['stage'],ev['percent'])
            elif 'directory' in ev:self.out=Path(ev['directory'])
            elif 'exit' in ev:
                self.pipe=None
                if ev['exit']:
                    self.setstatus('error',0);messagebox.showerror('GVC Explorer',ev['error'].strip().splitlines()[-1] if ev['error'].strip() else 'Worker stopped');[b.state(['!disabled']) for b in self.controls];return
                m=json.loads((self.out/'metadata.json').read_text(encoding='utf-8'));self.meta=m;self.r=result_at(self.out/'results.npz',m);self.view=default_view(self.r,m);self.page=self.out/'atlas.html';self.chart=0;self.setstatus('done',100);self.build();self.detail.set(str(self.out));return
        self.w.after(75,self.poll)
    def close(self):
        if self.pipe and self.pipe.poll() is None:
            if not messagebox.askyesno('GVC Explorer',self.tr('停止当前计算并关闭？','Stop the active run and close?')):return
            self.pipe.terminate()
        self.w.destroy()
if __name__=='__main__':
    root=tk.Tk();Workspace(root);root.mainloop()
