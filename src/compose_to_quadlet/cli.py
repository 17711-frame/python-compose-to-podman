# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from __future__ import annotations
import sys
import os
import re
import logging
import click
from typing import Optional, List
from .compose_parser import parse_compose_yaml
from .quadlet_writer import write_quadlets
from . import __version__
from .exceptions import VersionNotFoundError, VersionMismatchError, ComposeToQuadletError

# Set up logging
logger = logging.getLogger(__name__)

class VersionChecker:
    """A utility class to check for version consistency across project files."""

    def __init__(self, readme_path: str, pyproject_path: str, package_path: str) -> None:
        """Initializes the VersionChecker with paths to relevant files.

        Args:
            readme_path: The path to the README.md file.
            pyproject_path: The path to the pyproject.toml file.
            package_path: The path to the package's __init__.py file.
        """
        self.readme_path = readme_path
        self.pyproject_path = pyproject_path
        self.package_path = package_path

    def _get_version_from_pyproject(self) -> str:
        """Extracts the version from pyproject.toml.

        Returns:
            The version string.

        Raises:
            VersionNotFoundError: If the version is not found.
        """
        logger.debug(f"Attempting to get version from {self.pyproject_path}")
        with open(self.pyproject_path, "r", encoding="utf-8") as f:
            txt = f.read()
        m = re.search(r"version\s*=\s*\"([0-9]+\.[0-9]+\.[0-9]+)\"", txt)
        if not m:
            raise VersionNotFoundError(f"Version not found in {self.pyproject_path}")
        logger.debug(f"Found version {m.group(1)} in {self.pyproject_path}")
        return m.group(1)

    def _get_version_from_package(self) -> str:
        """Extracts the version from the package's __init__.py file.

        Returns:
            The version string.

        Raises:
            VersionNotFoundError: If __version__ is not found.
        """
        logger.debug(f"Attempting to get version from {self.package_path}")
        with open(self.package_path, "r", encoding="utf-8") as f:
            txt = f.read()
        m = re.search(r"__version__\s*=\s*\"(.*?)\"", txt)
        if not m:
            raise VersionNotFoundError(f"__version__ not found in {self.package_path}")
        logger.debug(f"Found version {m.group(1)} in {self.package_path}")
        return m.group(1)

    def _get_version_from_readme(self) -> Optional[str]:
        """Extracts the version from README.md.

        Returns:
            The version string if found, otherwise None.
        """
        logger.debug(f"Attempting to get version from {self.readme_path}")
        if not os.path.exists(self.readme_path):
            logger.debug(f"README file not found at {self.readme_path}")
            return None
        with open(self.readme_path, "r", encoding="utf-8") as f:
            txt = f.read()
        m = re.search(r"compose-to-quadlet v([0-9]+\.[0-9]+\.[0-9]+)", txt)
        if m:
            logger.debug(f"Found version {m.group(1)} in {self.readme_path}")
        else:
            logger.debug(f"Version not found in {self.readme_path}")
        return m.group(1) if m else None

    def check_versions(self) -> None:
        """Compares versions across pyproject.toml, __init__.py, and README.md.

        Raises:
            VersionMismatchError: If any version mismatch is found.
        """
        v_py = self._get_version_from_pyproject()
        v_pkg = self._get_version_from_package()
        v_rd = self._get_version_from_readme()

        if v_rd and (v_rd != v_py or v_rd != v_pkg):
            raise VersionMismatchError(f"Version mismatch: README={v_rd} pyproject={v_py} package={v_pkg}")
        if v_py != v_pkg:
            raise VersionMismatchError(f"Version mismatch: pyproject={v_py} package={v_pkg}")
        logger.info(f"Version OK: {v_py}")

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="compose-to-quadlet")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Enable verbose output.",
)
def main(verbose: bool) -> None:
    """Convert Docker/Podman Compose YAML to Podman Quadlet units.

    This CLI tool provides commands to convert Docker Compose files into
    Podman Quadlet unit files, facilitating the deployment of containerized
    applications with systemd.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    logger.debug(f"Logging level set to {logging.getLevelName(log_level)}")

@main.command("convert")
@click.argument("compose_file", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option("-o", "--output", "output_dir", type=click.Path(file_okay=False), default="./quadlets", show_default=True, help="Directory to write the Quadlet unit files.")
def convert_cmd(compose_file: str, output_dir: str) -> None:
    """Convert COMPOSE_FILE into Quadlet units in OUTPUT_DIR.

    Args:
        compose_file: Path to the input Docker Compose YAML file.
        output_dir: Directory where the generated Quadlet unit files will be saved.
    """
    logger.info(f"Converting Compose file: {compose_file} to Quadlet units in {output_dir}")
    try:
        with open(compose_file, "r", encoding="utf-8") as f:
            text = f.read()
        spec = parse_compose_yaml(text)
        paths = write_quadlets(spec, output_dir)
        logger.info(f"Wrote {len(paths)} quadlet files to {output_dir}")
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        sys.exit(1)

@main.command("version-check")
@click.option("--readme", default="README.md", show_default=True, help="Path to the README.md file.")
@click.option("--pyproject", default="pyproject.toml", show_default=True, help="Path to the pyproject.toml file.")
@click.option("--package", default="src/compose_to_quadlet/__init__.py", show_default=True, help="Path to the package's __init__.py file.")
def version_check_cmd(readme: str, pyproject: str, package: str) -> None:
    """Ensure version consistency across files.

    This command checks if the version specified in pyproject.toml, the package's
    __init__.py, and README.md are all consistent. It exits with an error if a
    mismatch is found.

    Args:
        readme: Path to the README.md file.
        pyproject: Path to the pyproject.toml file.
        package: Path to the package's __init__.py file.
    """
    logger.info("Checking version consistency...")
    try:
        checker = VersionChecker(readme, pyproject, package)
        checker.check_versions()
    except (VersionNotFoundError, VersionMismatchError) as e:
        logger.error(f"Version check failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred during version check: {e}")
        sys.exit(1)