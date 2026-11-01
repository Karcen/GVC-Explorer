"""Check startup dependency detection independently of the display server."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import ast
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location('studio_launcher', ROOT / 'run_all.py')
launcher = module_from_spec(spec)
spec.loader.exec_module(launcher)


def test_launcher_requirements_match_project():
    line, = (x for x in (ROOT / 'pyproject.toml').read_text().splitlines() if x.startswith('dependencies = '))
    assert tuple(ast.literal_eval(line.split('=', 1)[1].strip())) == launcher.REQUIRES


@pytest.mark.parametrize('installed,expected', [('1.24', True), ('1.23.9', False), ('3.0.0', False), (None, False)])
def test_versions(monkeypatch, installed, expected):
    real = launcher.metadata.version
    def distribution(name):
        if name == 'numpy':
            if installed is None:
                raise launcher.metadata.PackageNotFoundError(name)
            return installed
        return real(name)
    monkeypatch.setattr(launcher.metadata, 'version', distribution)
    assert launcher.compatible() == expected


def test_probe_current_python():
    assert launcher.probe(Path(sys.executable)) == launcher.compatible()
