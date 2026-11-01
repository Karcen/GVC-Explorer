"""OECD ICIO 2025 label mappings must not leak into incompatible matrices."""
import pytest
from gvc.metadata import load_oecd_icio_catalog, resolve_labels, OECD_ICIO_SCHEMA, oecd_metadata_template


def test_catalog_matches_attached_oecd_workbook():
    catalog = load_oecd_icio_catalog()
    assert catalog['edition'] == 2025
    assert len(catalog['economies']) == 85
    assert len(catalog['sectors']) == 50
    assert [(x['code'], x['name']) for x in catalog['economies'][:2]] == [
        ('AGO', 'Angola'), ('ARE', 'United Arab Emirates')]
    assert [x['code'] for x in catalog['economies'][-4:]] == ['MX1', 'MX2', 'CN1', 'CN2']
    assert catalog['sectors'][0]['code'] == 'A01'
    assert catalog['sectors'][-1]['code'] == 'T'
    assert catalog['sectors'][40]['name'] == 'Financial and insurance activities'


def test_2007_legacy_indices_must_not_claim_oecd_labels():
    names, industries, source = resolve_labels({}, 48, 17)
    assert names[0].startswith('Economy index')
    assert industries[0].startswith('Sector index')
    assert 'unverified' in source.lower()


def test_icio_mapping_requires_correct_shape_and_confirmed_order():
    with pytest.raises(ValueError, match='85 economies and 50 sectors'):
        resolve_labels({'classification': OECD_ICIO_SCHEMA, 'axis_order_confirmed': True}, 48, 17)
    with pytest.raises(ValueError, match='axis_order_confirmed'):
        resolve_labels({'classification': OECD_ICIO_SCHEMA}, 85, 50)


def test_icio_2025_labels_match_confirmed_order():
    catalog = load_oecd_icio_catalog()
    info = {
        'classification': OECD_ICIO_SCHEMA, 'axis_order_confirmed': True,
        'economy_codes': [r['code'] for r in catalog['economies']],
        'sector_codes': [r['code'] for r in catalog['sectors']],
    }
    names, industries, source = resolve_labels(info, 85, 50)
    assert names[14] == "CHN — China, People's Republic of"
    assert industries[40] == 'K — Financial and insurance activities'
    assert '2025' in source
    info['economy_codes'][0] = 'ARE'
    with pytest.raises(ValueError, match='economy_codes'):
        resolve_labels(info, 85, 50)


def test_explicit_custom_labels_are_preserved():
    names, sectors, source = resolve_labels({
        'country_names': ['A','B'], 'industry_names': ['C']
    }, 2, 1)
    assert (names, sectors) == (['A','B'],['C'])
    assert source == 'User-provided metadata.json'


def test_icio_requires_explicit_code_arrays_in_addition_to_flag():
    with pytest.raises(ValueError, match='economy_codes is required'):
        resolve_labels({'classification': OECD_ICIO_SCHEMA, 'axis_order_confirmed': True}, 85, 50)


def test_metadata_template_requires_manual_order_verification():
    template = oecd_metadata_template()
    assert template['classification'] == OECD_ICIO_SCHEMA
    assert template['axis_order_confirmed'] is False
    assert len(template['economy_codes']) == 85
    assert len(template['sector_codes']) == 50
    assert template['economy_codes'][:2] == ['AGO', 'ARE']
    assert template['sector_codes'][-1] == 'T'
    with pytest.raises(ValueError, match='axis_order_confirmed'):
        resolve_labels(template, 85, 50)
    template['axis_order_confirmed'] = True
    labels_e, labels_s, _ = resolve_labels(template, 85, 50)
    assert labels_e[22] == 'DEU — Germany'
    assert labels_s[20].startswith('C26 — Manufacture of computer')


def test_oecd_economy_major_row_and_col_codes():
    catalog = load_oecd_icio_catalog()
    ids = [f"{e['code']}_{s['code']}" for e in catalog['economies'] for s in catalog['sectors']]
    assert len(ids) == 4250
    assert len(set(ids)) == 4250
    assert ids[:2] == ['AGO_A01', 'AGO_A02']
    assert ids[-1] == 'CN2_T'
