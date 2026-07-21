# ppm

![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)

Gestor de dependencias para Python, inspirado en npm/pnpm. Usa `pip` por debajo.

## Instalación (global, recomendado con pipx)

```bash
git clone https://github.com/TU_USUARIO/ppm.git
cd ppm
pipx install -e .
# o, sin pipx:
pip install --user -e .
```

## Uso

```bash
mkdir mi-proyecto && cd mi-proyecto
ppm init                       # crea ppm.toml, .venv y ppm-lock.json

eval "$(ppm activate)"         # activa el venv en tu shell actual
                                # (autodetecta bash/zsh/fish vía $SHELL,
                                #  o forzá con --shell fish)

ppm install requests           # instala, agrega a ppm.toml y actualiza el lock
ppm install pytest --dev       # dependencia de desarrollo

ppm list                       # ver dependencias (directas vs transitivas)
ppm uninstall requests         # desinstala y limpia el manifiesto/lock

ppm export -o requirements.txt # exporta el lock a formato pip clásico

# En una máquina/CI nueva, para reproducir el entorno exacto del lock:
ppm init
eval "$(ppm activate)"
ppm install                    # sin argumentos = instala todo desde ppm-lock.json
```

## Archivos que genera

- `ppm.toml` — manifiesto: dependencias directas con rango de versión (fuente de verdad, lo editás vos indirectamente vía `ppm install`).
- `ppm-lock.json` — versiones exactas resueltas, directas y transitivas (no se edita a mano).
- `.venv/` — el entorno virtual del proyecto.

## Limitaciones conocidas del MVP (próximos pasos)

- `ppm uninstall` no limpia dependencias transitivas huérfanas — falta `ppm prune`.
- Todavía no detecta dependencias declaradas-pero-no-usadas en el código (`ppm check`, vía `ast`).
- No resuelve conflictos de versión entre paquetes (confía en el resolver de pip).
- Sin cache/store global compartido entre proyectos (estilo pnpm).

## Licencia

GPLv3 o posterior — ver [LICENSE](LICENSE).