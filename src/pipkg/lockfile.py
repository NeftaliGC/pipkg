# pipkg a gestor of pip dependencies
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

"""Lectura y escritura del lockfile pipkg-lock.json (equivalente a package-lock.json)."""

import json
from pathlib import Path

LOCK_NAME = "pipkg-lock.json"


def lock_path(root: Path) -> Path:
    return root / LOCK_NAME


def load_lock(root: Path) -> dict:
    path = lock_path(root)
    if not path.exists():
        return {"lockfile_version": 1, "dependencies": {}}
    return json.loads(path.read_text())


def save_lock(root: Path, data: dict) -> None:
    lock_path(root).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
