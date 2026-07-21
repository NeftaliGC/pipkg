# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - MVP - 2026-06-21

### Added
- `ppm init` crea el manifiesto (`ppm.toml`), el entorno virtual (`.venv`), el lock (`ppm-lock.json`) y un `.gitignore`. Es idempotente: si ya existe el manifiesto pero falta el venv (proyecto clonado), solo recrea el venv.
- `ppm activate` imprime el comando de activación del venv para usar con `eval "$(ppm activate)"`, con detección automática de shell (bash/zsh/fish).
- `ppm install <paquete>` instala con pip, actualiza el manifiesto y resuelve el lock completo (directas + transitivas) comparando el estado de `site-packages` antes/después.
- `ppm install` (sin argumentos) reproduce el entorno exacto desde `ppm-lock.json`; crea el venv automáticamente si no existe.
- `ppm uninstall <paquete>` desinstala y limpia manifiesto y lock.
- `ppm list` lista dependencias distinguiendo directas de transitivas.
- `ppm export` genera un `requirements.txt` reproducible con el árbol completo de versiones exactas.
- Manejo de errores limpio para fallos esperables de pip (sin traceback).
- Aviso cuando el `.venv` del proyecto no está activo en la shell actual.