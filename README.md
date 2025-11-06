# compose-to-quadlet

> Convert Docker / Podman Compose to Podman Quadlet units.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/compose-to-quadlet.svg)](https://pypi.org/project/compose-to-quadlet/)
[![Coverage](https://img.shields.io/badge/coverage-unknown-lightgrey.svg)](./coverage.svg)
[![Docs](https://img.shields.io/badge/docs-pdoc-green.svg)](https://17711.org/compose-to-quadlet/docs/)
[![Release](https://img.shields.io/github/v/release/17711/compose-to-quadlet)](https://github.com/17711/compose-to-quadlet/releases)

## Table of Contents
- [Synopsis](#synopsis)
- [Install](#install)
- [Usage](#usage)
- [Examples](#examples)
- [CI/CD](#cicd)
- [License](#license)
- [Credits & Open Source Notices](#credits--open-source-notices)
- [Contributing](#contributing)

## Synopsis
**compose-to-quadlet** converts Docker/Podman Compose YAML into Podman Quadlet units (`.container`, `.network`, `.volume`) using concise, typed Python models.

## Install
```bash
pipx install compose-to-quadlet
# or
poetry add compose-to-quadlet
```

## Usage
```bash
compose-to-quadlet --help
compose-to-quadlet convert examples/docker-compose.min.yml -o ./quadlets
```

## Examples
A minimal Docker Compose example is provided in `examples/docker-compose.min.yml`.

## CI/CD
This project ships a GitHub Actions workflow that lints, tests, builds, publishes to PyPI on tag push (`vX.Y.Z`), creates a GitHub Release with ZIP artifact, and deploys `pdoc` docs to GitHub Pages. Tags with suffixes like `-alpha`, `-beta`, `-rc` are treated as pre-releases.

## Documentation and Compliance
- International English, modern Python, strong typing, Pydantic validation.
- References:
  - Podman Quadlet documentation: https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html
  - Quadlet container units: https://docs.podman.io/en/latest/markdown/quadlet-container.5.html
  - Docker/Podman Compose reference: https://docs.docker.com/compose/compose-file/


### Sponsored by The 17711 Frame

<!-- Monero (XMR): `44AFFq5kSiGBoZ...` _(replace with your address)_ -->

## Credits & Open Source Notices
- click, pydantic, pyyaml, anyio, aiofiles, pytest, coverage, black, ruff, mypy, pdoc

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

> MIT © The 17711 Frame — https://17711.org
