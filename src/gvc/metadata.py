"""Verified OECD ICIO 2025 Extended labels and strict matrix-axis mapping.

Metadata are transcribed directly from the user-provided ReadMe_ICIO_extended.xlsx,
sheets Area_Activities, RowItems, and ColItems. Labels from the 2025 edition
must never be assigned by position to the unrelated 2007 48x17 dataset.
"""
from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
import json

OECD_ICIO_SCHEMA = 'OECD_ICIO_2025_EXTENDED'


@lru_cache(maxsize=1)
def load_oecd_icio_catalog() -> dict:
    """Load the OECD-published 2025 Extended dimension dictionary."""
    path = files('gvc').joinpath('data/oecd_icio_2025_extended.json')
    catalog = json.loads(path.read_text(encoding='utf-8'))
    assert len(catalog['economies']) == 85 and len(catalog['sectors']) == 50
    assert len({r['code'] for r in catalog['economies']}) == 85
    assert len({r['code'] for r in catalog['sectors']}) == 50
    assert all(r['position'] == i + 1 for i, r in enumerate(catalog['economies']))
    assert all(r['position'] == i + 1 for i, r in enumerate(catalog['sectors']))
    return catalog


def resolve_labels(metadata: dict, economies: int, sectors: int) -> tuple[list[str], list[str], str]:
    """Provide labels for a computed IO result without inferring source identity.

    Selecting OECD labels requires the exact 85x50 dimensions AND a positive
    axis-order confirmation. Optional explicit code arrays are checked against
    the source row/column ordering; mismatches fail rather than mislabeling data.
    """
    if metadata.get('classification') == OECD_ICIO_SCHEMA:
        catalog = load_oecd_icio_catalog()
        expected_economies = [item['code'] for item in catalog['economies']]
        expected_sectors = [item['code'] for item in catalog['sectors']]
        if (economies, sectors) != (len(expected_economies), len(expected_sectors)):
            raise ValueError('OECD ICIO 2025 Extended requires 85 economies and 50 sectors')
        if metadata.get('axis_order_confirmed') is not True:
            raise ValueError('OECD ICIO mapping requires axis_order_confirmed=true in metadata')
        for key, expected in [('economy_codes', expected_economies), ('sector_codes', expected_sectors)]:
            if key not in metadata:
                raise ValueError(f'{key} is required to verify the exact OECD 2025 RowItems / ColItems order')
            if metadata[key] != expected:
                raise ValueError(f'{key} does not match OECD 2025 RowItems / ColItems order')
        return (
            [f"{item['code']} — {item['name']}" for item in catalog['economies']],
            [f"{item['code']} — {item['name']}" for item in catalog['sectors']],
            'OECD ICIO 2025 Extended (confirmed code order)',
        )

    given_economies = metadata.get('country_names')
    given_sectors = metadata.get('industry_names')
    if given_economies is not None and len(given_economies) != economies:
        raise ValueError(f'country_names length {len(given_economies)} != {economies}')
    if given_sectors is not None and len(given_sectors) != sectors:
        raise ValueError(f'industry_names length {len(given_sectors)} != {sectors}')
    economy_labels = list(given_economies) if given_economies is not None else [f'Economy index {i+1:02d}' for i in range(economies)]
    sector_labels = list(given_sectors) if given_sectors is not None else [f'Sector index {i+1:02d}' for i in range(sectors)]
    source = 'User-provided metadata.json' if given_economies is not None and given_sectors is not None else 'Unverified index labels (source classification not established)'
    return economy_labels, sector_labels, source


def oecd_metadata_template() -> dict:
    """Full axis-order template; user must independently confirm matrix order."""
    catalog = load_oecd_icio_catalog()
    return {
        'classification': OECD_ICIO_SCHEMA,
        'axis_order_confirmed': False,
        'economy_codes': [r['code'] for r in catalog['economies']],
        'sector_codes': [r['code'] for r in catalog['sectors']],
        'unit': catalog['unit'],
        'year': None,
    }
