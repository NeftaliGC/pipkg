# pipkg - A manager for pip dependencies
# Copyright (C) 2026 Neftaligc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Creación del entorno virtual y todas las llamadas a pip pasan por acá."""

import json
import os
import subprocess
import sys
import venv as venv_module
from pathlib import Path

VENV_DIR = ".venv"


def venv_path(root: Path) -> Path:
    return root / VENV_DIR


def venv_python(root: Path) -> Path:
    v = venv_path(root)
    if sys.platform == "win32":
        return v / "Scripts" / "python.exe"
    return v / "bin" / "python"


def venv_exists(root: Path) -> bool:
    return venv_python(root).exists()


def is_active(root: Path) -> bool:
    """True si la shell actual tiene ESTE venv activo (según $VIRTUAL_ENV)."""
    active = os.environ.get("VIRTUAL_ENV")
    if not active:
        return False
    try:
        return Path(active).resolve() == venv_path(root).resolve()
    except OSError:
        return False


def create_venv(root: Path) -> None:
    venv_module.create(venv_path(root), with_pip=True)


def _run_pip(root: Path, args: list) -> subprocess.CompletedProcess:
    python = venv_python(root)
    if not python.exists():
        raise RuntimeError("No existe un entorno virtual. Corré 'pipkg init' primero.")
    return subprocess.run(
        [str(python), "-m", "pip", *args], capture_output=True, text=True
    )


def pip_install(root: Path, *specs: str) -> subprocess.CompletedProcess:
    return _run_pip(root, ["install", *specs])


def pip_uninstall(root: Path, name: str) -> subprocess.CompletedProcess:
    return _run_pip(root, ["uninstall", "-y", name])


def pip_list(root: Path) -> dict:
    result = _run_pip(root, ["list", "--format=json"])
    if result.returncode != 0:
        raise RuntimeError(f"pip list falló: {result.stderr}")
    return {pkg["name"].lower(): pkg["version"] for pkg in json.loads(result.stdout)}


def pip_show(root: Path, name: str) -> dict:
    result = _run_pip(root, ["show", name])
    if result.returncode != 0:
        raise RuntimeError(f"pip show {name} falló: {result.stderr}")
    info = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            info[key.strip()] = value.strip()
    requires = [r.strip() for r in info.get("Requires", "").split(",") if r.strip()]
    return {"version": info.get("Version", ""), "requires": requires}