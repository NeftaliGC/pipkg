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

"""Genera el comando de activación para usar con: eval "$(ppm activate)" """

import os
import sys
from pathlib import Path

from . import venv_utils


def _detect_shell() -> str:
    shell_path = os.environ.get("SHELL", "")
    return Path(shell_path).name or "bash"


def activation_command(root: Path, shell: str | None = None) -> str:
    if not venv_utils.venv_exists(root):
        raise RuntimeError("No existe un entorno virtual. Corré 'ppm init' primero.")

    v = venv_utils.venv_path(root)
    shell = shell or _detect_shell()

    if shell == "fish":
        return f"source {v / 'bin' / 'activate.fish'}"
    if shell in ("csh", "tcsh"):
        return f"source {v / 'bin' / 'activate.csh'}"
    if sys.platform == "win32":
        return f". {v / 'Scripts' / 'Activate.ps1'}"
    # bash / zsh / sh
    return f"source {v / 'bin' / 'activate'}"
