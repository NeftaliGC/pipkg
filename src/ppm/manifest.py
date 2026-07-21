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

"""Lectura y escritura del manifiesto ppm.toml (equivalente a package.json)."""

from pathlib import Path

import tomlkit

MANIFEST_NAME = "ppm.toml"


def manifest_path(root: Path) -> Path:
    return root / MANIFEST_NAME


def load_manifest(root: Path) -> tomlkit.TOMLDocument:
    path = manifest_path(root)
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró {MANIFEST_NAME} en {root}. Corré 'ppm init' primero."
        )
    return tomlkit.parse(path.read_text())


def save_manifest(root: Path, doc: tomlkit.TOMLDocument) -> None:
    manifest_path(root).write_text(tomlkit.dumps(doc))


def new_manifest(name: str, python_requires: str = ">=3.10") -> tomlkit.TOMLDocument:
    doc = tomlkit.document()

    project = tomlkit.table()
    project["name"] = name
    project["version"] = "0.1.0"
    project["python"] = python_requires
    doc["project"] = project

    doc["dependencies"] = tomlkit.table()
    doc["dev-dependencies"] = tomlkit.table()
    return doc


def add_dependency(doc: tomlkit.TOMLDocument, name: str, spec: str, dev: bool = False) -> None:
    section = "dev-dependencies" if dev else "dependencies"
    doc[section][name] = spec


def remove_dependency(doc: tomlkit.TOMLDocument, name: str) -> bool:
    removed = False
    for section in ("dependencies", "dev-dependencies"):
        if name in doc[section]:
            del doc[section][name]
            removed = True
    return removed
