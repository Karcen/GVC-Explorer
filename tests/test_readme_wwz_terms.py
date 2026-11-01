"""Check that the documented WWZ terms retain the source-code and paper numbering."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = "Wang, Z., Wei, S. J., & Zhu, K. (2013)."
TERMS = [
    "DVA_FIN", "DVA_INT", "DVA_INTrex1", "DVA_INTrex2", "DVA_INTrex3",
    "RDV_FIN1", "RDV_FIN2", "RDV_INT", "DDC_FIN", "DDC_INT",
    "MVA_FIN", "MVA_INT", "MDC", "OVA_FIN", "OVA_INT", "ODC",
]


def test_bilingual_readmes_define_all_16_terms_with_formulas():
    for filename in ("README.md", "README_EN.md"):
        document = (ROOT / filename).read_text(encoding="utf-8")
        matches = re.findall(r"^\*\*T(\d+) — ([^:：]+)[:：]", document, flags=re.MULTILINE)
        assert matches == [(str(i), label) for i, label in enumerate(TERMS, 1)], filename
        formula_labels = re.findall(r"^T_\{?(\d+)\}?\^\{sr\}", document, flags=re.MULTILINE)
        assert formula_labels == [str(i) for i in range(1, 17)], filename
        assert PAPER in document, filename
        assert document.count("$$") == 34, filename  # 16 terms + export identity
        assert "valueadded2007.m" in document, filename
        assert "https://www.nber.org/papers/w19677" in document, filename
