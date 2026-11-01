"""Verify actual delivery files, not their configured export settings. Requires PyMuPDF and Pillow."""
from pathlib import Path
import json
from xml.etree import ElementTree as ET
import fitz
from PIL import Image,ImageOps,ImageDraw,ImageFilter
import numpy as np
P=Path(__file__).resolve().parents[1]; rows=[];gallery=Image.new('RGB',(1200,1000),'white');d=ImageDraw.Draw(gallery)
for lang in ('en','zh'):
    for i,path in enumerate(sorted((P/'reports/atlas_2007'/lang).glob('*.pdf'))):
        with fitz.open(path) as doc:
            assert len(doc)==1; p=doc[0];w,h=p.rect.width,p.rect.height;text=p.get_text('dict');spans=[s for b in text['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans'] if s['text'].strip()]; pix=p.get_pixmap(matrix=fitz.Matrix(1,1));img=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).resize((294,190)); j=(0 if lang=='en' else 8)+i;gallery.paste(img,(300*(j%4),244*(j//4)));d.text((300*(j%4)+6,244*(j//4)+194),lang+'/'+path.stem,fill='black');
            assert abs(w*25.4/72-183)<.02 and abs(h*25.4/72-116)<.02; outside=[s['text'] for s in spans if min(s['bbox'][:2])<-.1 or s['bbox'][2]>w+.1 or s['bbox'][3]>h+.1]; assert not outside,(path,outside); assert min(s['size'] for s in spans)>6.4
            assert p.get_fonts() and all('Type3' not in font for f in p.get_fonts() for font in map(str,f));svg=ET.parse(path.with_suffix('.svg'));assert list(svg.getroot().iter('{http://www.w3.org/2000/svg}text'));assert path.with_suffix('.csv').stat().st_size>10
            with Image.open(path.with_suffix('.png')) as im: dpi=im.info['dpi'];assert all(abs(x-450)<.1 for x in dpi)
            pix=p.get_pixmap(matrix=fitz.Matrix(1.7,1.7));title_pdf=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).convert('L');sw,sh=title_pdf.size;box=(int(sw*.053),int(sh*.08),int(sw*.96),int(sh*.15));title_png=Image.open(path.with_suffix('.png')).convert('L').resize((sw,sh),Image.Resampling.LANCZOS);v1,v2=[np.asarray(q.crop(box).filter(ImageFilter.GaussianBlur(1)),dtype=float).ravel() for q in (title_pdf,title_png)];rho=float(np.corrcoef(v1,v2)[0,1]);assert rho>.92,(path,rho)
            rows.append(dict(rendered_title_agreement=round(rho,4),name=lang+'/'+path.stem,text_blocks=len(spans),min_actual_pt=round(min(s['size'] for s in spans),2),bounds_pass=True,page_mm=[183,116],png_dpi=450,editable_svg_text=True))
assert len(rows)==16;gallery.save(P/'reports/figure_contact_sheet.png');(P/'reports/figure_qa.json').write_text(json.dumps({'runtime':'PyMuPDF PDF geometry and embedded fonts; Pillow PNG; SVG XML','figures':rows},indent=2));print('OK: 16 figure sets, 2 languages, 3 formats')
