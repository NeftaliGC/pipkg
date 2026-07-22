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

import argparse
import sys
from pathlib import Path

from . import activate, lockfile, manifest, resolver, venv_utils


def cmd_init(args):
    root = Path.cwd()

    if manifest.manifest_path(root).exists():
        if venv_utils.venv_exists(root):
            print(f"Ya existe {manifest.MANIFEST_NAME} y .venv en este directorio. No hay nada que hacer.")
            return
        # pipkg.toml existe pero falta el venv: probablemente un proyecto recién clonado.
        print(f"Ya existe {manifest.MANIFEST_NAME} pero falta el entorno virtual (¿proyecto clonado?).")
        print("Creando entorno virtual en .venv ...")
        venv_utils.create_venv(root)
        if not lockfile.lock_path(root).exists():
            lockfile.save_lock(root, {"lockfile_version": 1, "dependencies": {}})
        print()
        print("Entorno creado. Ahora corré:")
        print('  eval "$(pipkg activate)"')
        print("  pipkg install")
        return

    name = args.name or root.name
    doc = manifest.new_manifest(name)
    manifest.save_manifest(root, doc)

    print("Creando entorno virtual en .venv ...")
    venv_utils.create_venv(root)

    lockfile.save_lock(root, {"lockfile_version": 1, "dependencies": {}})
    _ensure_gitignore(root)

    print(f"Proyecto '{name}' inicializado.")
    print()
    print("Para activar el entorno, corré:")
    print('  eval "$(pipkg activate)"')


def _ensure_gitignore(root: Path) -> None:
    gitignore = root / ".gitignore"
    entry = f"{venv_utils.VENV_DIR}/"
    if gitignore.exists():
        content = gitignore.read_text()
        if entry in content.splitlines():
            return
        gitignore.write_text(content.rstrip("\n") + f"\n{entry}\n")
    else:
        gitignore.write_text(f"{entry}\n")


def cmd_activate(args):
    root = Path.cwd()
    try:
        print(activate.activation_command(root, shell=args.shell))
    except RuntimeError as e:
        print(f"echo '{e}' 1>&2", file=sys.stderr)
        sys.exit(1)


def cmd_install(args):
    root = Path.cwd()
    if not manifest.manifest_path(root).exists():
        print(f"No se encontró {manifest.MANIFEST_NAME}. Corré 'pipkg init' primero.", file=sys.stderr)
        sys.exit(1)

    if not venv_utils.venv_exists(root):
        print("No hay entorno virtual todavía, creando .venv ...")
        venv_utils.create_venv(root)

    if not venv_utils.is_active(root):
        print(
            "Aviso: .venv no está activo en esta shell. Las dependencias se instalan "
            "igual, pero para USARLAS corré: eval \"$(pipkg activate)\"",
            file=sys.stderr,
        )

    if not args.package:
        print("Instalando dependencias desde pipkg-lock.json ...")
        specs = resolver.sync(root)
        print(f"{len(specs)} paquete(s) instalado(s).")
        return

    for package_spec in args.package:
        print(f"Instalando {package_spec} ...")
        name, version = resolver.install(root, package_spec, dev=args.dev)
        doc = manifest.load_manifest(root)
        manifest.add_dependency(doc, name, f">={version}", dev=args.dev)
        manifest.save_manifest(root, doc)
        print(f"  + {name}=={version}")


def cmd_uninstall(args):
    root = Path.cwd()
    for name in args.package:
        normalized = resolver.uninstall(root, name)
        doc = manifest.load_manifest(root)
        manifest.remove_dependency(doc, normalized)
        manifest.save_manifest(root, doc)
        print(f"  - {normalized}")


def cmd_list(args):
    root = Path.cwd()
    lock = lockfile.load_lock(root)
    deps = lock["dependencies"]
    if not deps:
        print("No hay dependencias instaladas.")
        return
    for name, info in sorted(deps.items()):
        tag = "directa" if info.get("direct") else "transitiva"
        dev_tag = ", dev" if info.get("dev") else ""
        print(f"{name}=={info['version']}  ({tag}{dev_tag})")


def cmd_export(args):
    root = Path.cwd()
    lock = lockfile.load_lock(root)
    lines = [f"{name}=={info['version']}" for name, info in sorted(lock["dependencies"].items())]
    output = "\n".join(lines) + ("\n" if lines else "")
    if args.output:
        Path(args.output).write_text(output)
        print(f"Exportado a {args.output}")
    else:
        print(output, end="")


def main():
    parser = argparse.ArgumentParser(
        prog="pipkg", description="Gestor de dependencias para Python (usa pip por debajo)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Inicializa un nuevo proyecto")
    p_init.add_argument("name", nargs="?", help="Nombre del proyecto (default: nombre de la carpeta)")
    p_init.set_defaults(func=cmd_init)

    p_activate = sub.add_parser("activate", help="Imprime el comando para activar el entorno")
    p_activate.add_argument("--shell", help="Forzar shell (bash, zsh, fish)")
    p_activate.set_defaults(func=cmd_activate)

    p_install = sub.add_parser("install", help="Instala un paquete, o todo lo del lock si no se pasa ninguno")
    p_install.add_argument("package", nargs="*", help="Ej: requests  o  'requests>=2.30'")
    p_install.add_argument("--dev", action="store_true", help="Marcar como dependencia de desarrollo")
    p_install.set_defaults(func=cmd_install)

    p_uninstall = sub.add_parser("uninstall", help="Desinstala uno o más paquetes")
    p_uninstall.add_argument("package", nargs="+")
    p_uninstall.set_defaults(func=cmd_uninstall)

    p_list = sub.add_parser("list", help="Lista las dependencias del proyecto")
    p_list.set_defaults(func=cmd_list)

    p_export = sub.add_parser("export", help="Exporta el lock a formato requirements.txt")
    p_export.add_argument("-o", "--output", help="Archivo de salida (default: stdout)")
    p_export.set_defaults(func=cmd_export)

    args = parser.parse_args()
    try:
        args.func(args)
    except (RuntimeError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()