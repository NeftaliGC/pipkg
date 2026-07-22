# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-06-22

### Changed
- Renamed project from **ppm** to **pipkg** to avoid collisions with existing projects.
- All commands and files have been renamed accordingly:
  - `ppm` → `pipkg`
  - `ppm.toml` → `pipkg.toml`
  - `ppm-lock.json` → `pipkg-lock.json`

## [0.1.0] - 2026-06-21

Initial MVP release.

### Added
* `ppm init` creates the project manifest (`ppm.toml`), virtual environment (`.venv`), lock file (`ppm-lock.json`), and a `.gitignore`. It is idempotent: if the manifest already exists but the virtual environment is missing (e.g., in a cloned repository), it only recreates the virtual environment.
* `ppm activate` prints the virtual environment activation command to be used with `eval "$(ppm activate)"`, with automatic shell detection (bash/zsh/fish).
* `ppm install <package>` installs the package with pip, updates the manifest, and resolves the complete lock file (direct and transitive dependencies) by comparing the state of `site-packages` before and after the installation.
* `ppm install` (without arguments) reproduces the exact environment from `ppm-lock.json`; it automatically creates the virtual environment if it does not exist.
* `ppm uninstall <package>` uninstalls a package and updates both the manifest and the lock file.
* `ppm list` lists dependencies, distinguishing between direct and transitive dependencies.
* `ppm export` generates a reproducible `requirements.txt` containing the complete dependency tree with pinned versions.
* Clean error handling for expected pip failures (no Python traceback).
* Warns when the project's `.venv` is not active in the current shell.
