import sys,time,tkinter as tk,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P))
import desktop as d
errors=[];d.messagebox.showerror=lambda title,msg:errors.append(msg)
w=tk.Tk();a=d.Workspace(w);w.update();assert a.meta['areas'][0]['en']=='Australia';a.switch();w.update();assert a.lang=='en';a.boxes[3].current(4);a.changed(None);w.update();assert a.chart==4
from PIL import ImageGrab
ImageGrab.grab(bbox=(w.winfo_rootx(),w.winfo_rooty(),w.winfo_rootx()+w.winfo_width(),w.winfo_rooty()+w.winfo_height())).save(P/'reports/studio_en.png');from tempfile import TemporaryDirectory
tmp=TemporaryDirectory();a.base=Path(tmp.name);a.start(P/'examples/fixture_3area_3sector.csv');deadline=time.monotonic()+110
while a.pipe is not None and time.monotonic()<deadline:w.update();time.sleep(.025)
assert not errors,errors;assert a.status==('done',100),a.status;assert a.r.countries==3 and a.r.sectors==3;assert a.page.is_file() and len(list((a.out/'figures').glob('*.pdf')))==8;a.switch();w.update();assert a.lang=='zh';w.destroy();(P/'reports/desktop_qa.json').write_text(json.dumps({'runtime':'Tk under Linux/Xvfb','switch_languages':True,'switch_chart':True,'import_via_desktop_worker':'fixture_3area_3sector.csv','exit_status':0,'formats_verified':['pdf','png','svg'],'auto_open_results':True},indent=2));tmp.cleanup();print('OK')
