"""Run this file in a Python editor to open GVC Explorer. No shell script is needed."""
from __future__ import annotations

import os
import runpy
import subprocess
import sys
from importlib import metadata
from pathlib import Path
from tempfile import NamedTemporaryFile

ROOT = Path(__file__).resolve().parent
# Check dependency versions without importing the scientific or GUI modules.
# The launcher test checks these against pyproject.toml.
REQUIRES = ("numpy>=1.24,<3", "scipy>=1.10,<2", "lxml>=4.9,<7", "pandas>=2,<3",
            "plotly>=5,<7", "matplotlib>=3.7,<4", "fonttools>=4.39,<5")
PROBE_MISSING = 3


def compatible() -> bool:
    """Inspect distribution metadata without importing large scientific libraries."""
    if sys.version_info < (3, 10):
        return False
    try:
        from packaging.requirements import Requirement  # Matplotlib runtime dependency
    except ModuleNotFoundError as exc:
        if exc.name != 'packaging':
            raise
        return False
    for spec in REQUIRES:
        req = Requirement(spec)
        try:
            installed = metadata.version(req.name)
        except metadata.PackageNotFoundError:
            return False
        if not req.specifier.contains(installed):
            return False
    return True


def project_python() -> Path:
    return ROOT / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def probe(python: Path) -> bool:
    result = subprocess.run([str(python), str(ROOT / 'run_all.py'), '--probe'], cwd=ROOT)
    if result.returncode not in (0, PROBE_MISSING):
        result.check_returncode()
    return result.returncode == 0


def install(root, python: Path) -> bool:
    """Ask before installing. Run venv and pip without blocking Tk's event loop."""
    import tkinter as tk
    from tkinter import ttk, messagebox

    # The launcher may be run from an IDE outside the project directory.
    sys.path.insert(0, str(ROOT))
    from ui_theme import apply
    apply(root)
    if not messagebox.askokcancel('GVC Explorer',
            '当前环境缺少依赖或版本不符。将依赖安装到项目的 .venv？不会修改系统 Python。\n\n'
            'Install the required packages in this project’s .venv? System Python stays unchanged.', parent=root):
        return False
    commands = []
    if not python.exists():
        commands.append(('创建环境 / Creating environment', [sys.executable, '-m', 'venv', str(ROOT / '.venv')]))
    commands.append(('安装依赖 / Installing packages',
                     [str(python), '-m', 'pip', '--disable-pip-version-check', 'install', *REQUIRES]))
    root.title('GVC Explorer · Setup'); root.resizable(False, False)
    frame = ttk.Frame(root, padding=20); frame.pack(fill='both', expand=True)
    label = ttk.Label(frame); label.pack(anchor='w')
    bar = ttk.Progressbar(frame, length=380, mode='indeterminate'); bar.pack(pady=12); bar.start()
    root.deiconify()
    with NamedTemporaryFile(mode='wb', prefix='gvc-setup-', suffix='.log', delete=False) as log:
        ttk.Label(frame, text=log.name, wraplength=380).pack(anchor='w')
        for stage, command in commands:
            label.configure(text=stage)
            child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            done = tk.BooleanVar(master=root, value=False)
            cancelled = False

            def cancel():
                nonlocal cancelled
                if child.poll() is None:
                    child.terminate()
                    cancelled = True

            def poll():
                if child.poll() is None:
                    root.after(125, poll)
                else:
                    done.set(True)

            root.protocol('WM_DELETE_WINDOW', cancel)
            root.after(0, poll); root.wait_variable(done)
            if cancelled:
                return False
            if child.returncode:
                raise RuntimeError(f'{stage}\n退出码 / Exit code: {child.returncode}\n日志 / Log: {log.name}')
    root.withdraw()
    if not probe(python):
        raise RuntimeError(f'安装后版本检查未通过。 / Requirements not met after installation.\n{log.name}')
    return True


def main() -> int:
    if sys.version_info < (3, 10):
        raise SystemExit('请选择 Python 3.10 或更新版本。 / Select Python 3.10 or later.')
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError as exc:
        raise SystemExit('当前解释器没有 Tk。请选择带 Tk 的 Python，再运行本文件。\n'
                         'Select a Python installation with Tk; pip cannot install tkinter.') from exc
    root = tk.Tk(); root.withdraw()
    try:
        for name in ('desktop.py', 'ui_theme.py', 'src/gvc', 'output/wwz_python_2007.npz'):
            if not (ROOT / name).exists():
                raise FileNotFoundError('请解压完整项目，把 run_all.py 放在 desktop.py 同一目录。\n'
                                        f'Extract the complete project. Missing: {ROOT / name}')
        use_current = compatible()
        if not use_current:
            python = project_python()
            if not (python.is_file() and probe(python)) and not install(root, python):
                return 0
            subprocess.run([str(python), str(ROOT / 'desktop.py')], cwd=ROOT, check=True)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        messagebox.showerror('GVC Explorer', str(exc), parent=root)
        raise
    finally:
        root.destroy()
    if use_current:
        sys.path.insert(0, str(ROOT))
        runpy.run_path(str(ROOT / 'desktop.py'), run_name='__main__')
    return 0


if __name__ == '__main__':
    if sys.argv[1:] == ['--probe']:
        raise SystemExit(0 if compatible() else PROBE_MISSING)
    raise SystemExit(main())
