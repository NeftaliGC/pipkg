# <ppm a gestor of pip dependencies>
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

"""Orquesta pip + lockfile: instalar, desinstalar y reproducir el entorno."""

import re
from pathlib import Path

from . import lockfile, venv_utils

_NAME_SPLIT = re.compile(r"[=<>!~\[]")


def _normalize(name: str) -> str:
    return name.lower().replace("_", "-")


def _package_name(spec: str) -> str:
    """De 'requests>=2.30' o 'requests[socks]' devuelve 'requests'."""
    return _normalize(_NAME_SPLIT.split(spec, 1)[0].strip())


def install(root: Path, package_spec: str, dev: bool = False):
    """
    Instala package_spec (ej. 'requests' o 'requests>=2.30') con pip dentro del
    venv del proyecto, y actualiza ppm-lock.json con todo lo nuevo que haya
    quedado instalado (directo + transitivas), comparando el estado de
    site-packages antes y después.

    Devuelve (nombre_normalizado, version_instalada).
    """
    requested_name = _package_name(package_spec)

    before = venv_utils.pip_list(root)
    result = venv_utils.pip_install(root, package_spec)
    if result.returncode != 0:
        raise RuntimeError(f"pip install falló:\n{result.stderr}")
    after = venv_utils.pip_list(root)

    lock = lockfile.load_lock(root)
    deps = lock["dependencies"]

    changed = {name: ver for name, ver in after.items() if before.get(name) != ver}

    for name, version in changed.items():
        info = venv_utils.pip_show(root, name)
        entry = deps.get(name, {})
        entry["version"] = version
        entry["requires"] = [_normalize(r) for r in info["requires"]]
        entry["direct"] = entry.get("direct", False) or (name == requested_name)
        entry["dev"] = entry.get("dev", False) or (dev and name == requested_name)
        deps[name] = entry

    lockfile.save_lock(root, lock)
    installed_version = after.get(requested_name, deps.get(requested_name, {}).get("version", ""))
    return requested_name, installed_version


def uninstall(root: Path, name: str) -> str:
    """Desinstala un paquete y lo saca del lock. No limpia transitivas huérfanas
    (eso queda para 'ppm prune' más adelante)."""
    normalized = _normalize(name)
    result = venv_utils.pip_uninstall(root, normalized)
    if result.returncode != 0:
        raise RuntimeError(f"pip uninstall falló:\n{result.stderr}")

    lock = lockfile.load_lock(root)
    lock["dependencies"].pop(normalized, None)
    lockfile.save_lock(root, lock)
    return normalized


def sync(root: Path):
    """Instala en el venv exactamente lo que dice ppm-lock.json (reproducibilidad,
    equivalente a 'npm install' sin argumentos usando el lock existente)."""
    lock = lockfile.load_lock(root)
    specs = [f"{name}=={info['version']}" for name, info in lock["dependencies"].items()]
    if not specs:
        return []

    result = venv_utils.pip_install(root, *specs)
    if result.returncode != 0:
        raise RuntimeError(f"pip install falló durante sync:\n{result.stderr}")
    return specs
