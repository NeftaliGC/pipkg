# pipkg

![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)

Gestor de dependencias para Python, inspirado en npm/pnpm. Usa `pip` por debajo.

## Instalación (global, recomendado con pipx)

```bash
git clone https://github.com/NeftaliGC/pipkg.git
cd pipkg
pipx install -e .
# o, sin pipx:
pip install --user -e .
```

## Uso

```bash
mkdir mi-proyecto && cd mi-proyecto
pipkg init                       # crea pipkg.toml, .venv y pipkg-lock.json

eval "$(pipkg activate)"         # activa el venv en tu shell actual
                                # (autodetecta bash/zsh/fish vía $SHELL,
                                #  o forzá con --shell fish)

pipkg install requests           # instala, agrega a pipkg.toml y actualiza el lock
pipkg install pytest --dev       # dependencia de desarrollo

pipkg list                       # ver dependencias (directas vs transitivas)
pipkg uninstall requests         # desinstala y limpia el manifiesto/lock

pipkg export -o requirements.txt # exporta el lock a formato pip clásico

# En una máquina/CI nueva, para reproducir el entorno exacto del lock:
pipkg init
eval "$(pipkg activate)"
pipkg install                    # sin argumentos = instala todo desde pipkg-lock.json
```

## Archivos que genera

- `pipkg.toml` — manifiesto: dependencias directas con rango de versión (fuente de verdad, lo editás vos indirectamente vía `pipkg install`).
- `pipkg-lock.json` — versiones exactas resueltas, directas y transitivas (no se edita a mano).
- `.venv/` — el entorno virtual del proyecto.

## Limitaciones conocidas del MVP (próximos pasos)

- `pipkg uninstall` no limpia dependencias transitivas huérfanas — falta `pipkg prune`.
- Todavía no detecta dependencias declaradas-pero-no-usadas en el código (`pipkg check`, vía `ast`).
- No resuelve conflictos de versión entre paquetes (confía en el resolver de pip).
- Sin cache/store global compartido entre proyectos (estilo pnpm).

## Licencia

GPLv3 o posterior — ver [LICENSE](https://github.com/NeftaliGC/pipkg/blob/main/LICENCE).