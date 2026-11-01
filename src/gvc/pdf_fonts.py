"""Embed only the plotted glyphs from a CFF system face as TrueType contours.

Some Matplotlib releases label CFF collections as CIDFontType2 in PDFs. Text
extracts correctly but several PDF viewers draw unrelated glyphs. Keep the
original system typeface for screen/SVG; use a temporary, equivalent quadratic
outline subset only for PDF and remove it after export. No font files ship.
"""
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from copy import copy
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from matplotlib import font_manager
from matplotlib.text import Text


def _embed_face(source, codepoints, out):
    """Return True when a CFF font needs a compatible temporary face."""
    with TTFont(source, fontNumber=0, lazy=True) as ft:
        if 'glyf' in ft:
            return False
        if 'CFF ' not in ft and 'CFF2' not in ft:
            raise ValueError(f'Unsupported PDF font outlines: {source}')
        licence=ft['OS/2'].fsType
        if licence & (0x2|0x0100|0x0200):
            raise ValueError(f'Subset embedding is not permitted for {source}. Choose another system font.')
        sub=subset.Subsetter();sub.populate(unicodes=codepoints);sub.subset(ft)
        cmap=ft.getBestCmap();names=ft.getGlyphOrder();gs=ft.getGlyphSet();upm=ft['head'].unitsPerEm
        glyphs={}
        for name in names:
            pen=TTGlyphPen(None);gs[name].draw(Cu2QuPen(pen,upm/1500,reverse_direction=True));glyphs[name]=pen.glyph()
        dst=FontBuilder(upm,isTTF=True);dst.setupGlyphOrder(names);dst.setupCharacterMap(cmap);dst.setupGlyf(glyphs);dst.setupHorizontalMetrics({n:ft['hmtx'][n] for n in names});dst.setupHorizontalHeader(ascent=ft['hhea'].ascent,descent=ft['hhea'].descent,lineGap=ft['hhea'].lineGap)
        ps='GVCSubset'+out.stem;dst.setupNameTable({'familyName':ps,'styleName':'Regular','fullName':ps,'psName':ps,'uniqueFontIdentifier':ps});o=ft['OS/2'];dst.setupOS2(sTypoAscender=o.sTypoAscender,sTypoDescender=o.sTypoDescender,usWinAscent=o.usWinAscent,usWinDescent=o.usWinDescent,fsType=licence);dst.setupPost();dst.setupMaxp();dst.save(out);return True


@contextmanager
def pdf_faces(fig):
    fig.canvas.draw();groups=defaultdict(list);originals=[]
    for text in fig.findobj(Text):
        if text.get_visible() and text.get_text():groups[font_manager.findfont(text.get_fontproperties())].append(text)
    with TemporaryDirectory(prefix='gvc-pdf-glyphs-') as tmp:
        try:
            for i,(src,texts) in enumerate(groups.items()):
                name=Path(tmp)/f'Face{i}.ttf';codepoints=set(range(32,127))|{0x2212}|{ord(c) for t in texts for c in t.get_text()}
                if _embed_face(src,codepoints,name):
                    for t in texts:
                        old=copy(t.get_fontproperties());new=copy(old);new.set_file(str(name));originals.append((t,old));t.set_fontproperties(new)
            yield
        finally:
            for t,old in originals:t.set_fontproperties(old)
