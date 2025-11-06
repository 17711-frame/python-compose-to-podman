# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
import pytest
from click.testing import CliRunner
from compose_to_quadlet.cli import main # Import the main Click group
import os
import logging

def test_version_check_ok(tmp_path, caplog):
    """Test that version check passes when versions are consistent."""
    caplog.set_level(logging.INFO)
    # Create dummy files with consistent versions
    pyproject_content = '[tool.poetry]\nname = "compose-to-quadlet"\nversion = "0.1.0"'
    readme_content = '# compose-to-quadlet\n\ncompose-to-quadlet v0.1.0'
    package_content = '__version__ = "0.1.0"'

    (tmp_path / "pyproject.toml").write_text(pyproject_content)
    (tmp_path / "README.md").write_text(readme_content)
    (tmp_path / "__init__.py").write_text(package_content)

    runner = CliRunner()
    result = runner.invoke(main, [
        "version-check", # Invoke the subcommand
        "--pyproject", (tmp_path / "pyproject.toml").as_posix(),
        "--readme", (tmp_path / "README.md").as_posix(),
        "--package", (tmp_path / "__init__.py").as_posix(),
    ])
    assert result.exit_code == 0
    assert any(r.levelname == "INFO" and r.message == "Version OK: 0.1.0" for r in caplog.records)

def test_version_check_mismatch(tmp_path, caplog):
    """Test that version check fails when versions are inconsistent."""
    caplog.set_level(logging.INFO)
    # Create dummy files with inconsistent versions
    pyproject_content = '[tool.poetry]\nname = "compose-to-quadlet"\nversion = "0.1.0"'
    readme_content = '# compose-to-quadlet\n\ncompose-to-quadlet v0.1.1' # Mismatch here
    package_content = '__version__ = "0.1.0"'

    (tmp_path / "pyproject.toml").write_text(pyproject_content)
    (tmp_path / "README.md").write_text(readme_content)
    (tmp_path / "__init__.py").write_text(package_content)

    runner = CliRunner()
    result = runner.invoke(main, [
        "version-check", # Invoke the subcommand
        "--pyproject", (tmp_path / "pyproject.toml").as_posix(),
        "--readme", (tmp_path / "README.md").as_posix(),
        "--package", (tmp_path / "__init__.py").as_posix(),
    ])
    assert result.exit_code != 0
    assert any(r.levelname == "ERROR" and r.message == "Version check failed: Version mismatch: README=0.1.1 pyproject=0.1.0 package=0.1.0" for r in caplog.records)

def test_version_check_no_readme(tmp_path, caplog):
    """Test that version check passes when README.md is missing but other versions match."""
    caplog.set_level(logging.INFO)
    # Test when README.md is missing
    pyproject_content = '[tool.poetry]\nname = "compose-to-quadlet"\nversion = "0.1.0"'
    package_content = '__version__ = "0.1.0"'

    (tmp_path / "pyproject.toml").write_text(pyproject_content)
    # No README.md file is created
    (tmp_path / "__init__.py").write_text(package_content)

    runner = CliRunner()
    result = runner.invoke(main, [
        "version-check", # Invoke the subcommand
        "--pyproject", (tmp_path / "pyproject.toml").as_posix(),
        "--readme", (tmp_path / "non_existent_README.md").as_posix(), # Point to a non-existent file
        "--package", (tmp_path / "__init__.py").as_posix(),
    ])
    assert result.exit_code == 0
    assert any(r.levelname == "INFO" and r.message == "Version OK: 0.1.0" for r in caplog.records)