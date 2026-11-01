"""Regressions for shipped pages and their generators; no browser required."""
from pathlib import Path
from lxml import html
import ast
from configparser import ConfigParser
ROOT=Path(__file__).resolve().parents[1]


def test_handbooks_use_generated_styles_and_literal_notice():
    css=(ROOT/'src/gvc/web/methods.css').read_text(encoding='utf8')
    for lang in ('en','zh'):
        d=html.parse(ROOT/f'docs/formulas_{lang}.html')
        assert d.xpath('//style/text()')==[css]
        assert d.xpath('//header/small/text()')==['For research only']
        assert d.xpath('//meta[@name="color-scheme"]/@content')==['light']


def test_atlas_styles_and_controls_ship_in_output():
    web=ROOT/'src/gvc/web';out=(ROOT/'offline_dashboard.html').read_text(encoding='utf8')
    for asset in ('app.js','design.css'):
        assert (web/asset).read_text(encoding='utf8') in out
    source=(web/'template.html').read_text(encoding='utf8')
    assert 'For research only' in source and 'id="theme"' not in source
    assert 'atlas-theme' not in (web/'app.js').read_text(encoding='utf8')


def test_legacy_view_sets_light_palette_for_all_plotly_charts():
    # ConfigParser suffices for these quoted string keys, including on Python 3.10.
    cfg=ConfigParser();cfg.read(ROOT/'.streamlit/config.toml');assert cfg['theme']['base'].strip('"')=='light'
    code=ast.parse((ROOT/'app.py').read_text(encoding='utf8'))
    helper=next(n for n in code.body if isinstance(n,ast.FunctionDef) and n.name=='show_chart')
    calls=[n for n in ast.walk(code) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='plotly_chart']
    assert len(calls)==1 and calls[0] in list(ast.walk(helper))
