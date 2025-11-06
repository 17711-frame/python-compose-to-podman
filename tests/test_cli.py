# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
import pytest
from click.testing import CliRunner
from compose_to_quadlet.cli import main
from unittest.mock import patch
import logging

@patch("compose_to_quadlet.cli.write_quadlets")
def test_convert_cmd_basic_flow(mock_write_quadlets, tmp_path, caplog):
    """Test the basic flow of the convert command with mocked file writes."""
    caplog.set_level(logging.INFO)
    compose_content = """
services:
  web:
    image: nginx
    ports:
      - "80:80"
"""
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text(compose_content)
    output_dir = tmp_path / "quadlets"
    mock_write_quadlets.return_value = [str(output_dir / "web.container")]

    runner = CliRunner()
    result = runner.invoke(main, ["convert", str(compose_file), "-o", str(output_dir)])

    assert result.exit_code == 0
    mock_write_quadlets.assert_called_once()
    assert any(r.levelname == "INFO" and "Wrote 1 quadlet files to" in r.message for r in caplog.records)

def test_version_check_pyproject_not_found(tmp_path, caplog):
    """Test VersionChecker when pyproject.toml is missing version."""
    caplog.set_level(logging.INFO)
    (tmp_path / "pyproject.toml").write_text("[tool.poetry]\nname = \"compose-to-quadlet\"")
    (tmp_path / "__init__.py").write_text("__version__ = \"0.1.0\"")
    (tmp_path / "README.md").write_text("# compose-to-quadlet\n\ncompose-to-quadlet v0.1.0")

    runner = CliRunner()
    result = runner.invoke(main, [
        "version-check",
        "--pyproject", str(tmp_path / "pyproject.toml"),
        "--package", str(tmp_path / "__init__.py"),
        "--readme", str(tmp_path / "README.md"),
    ])
    assert result.exit_code != 0
    assert any(r.levelname == "ERROR" and "Version check failed: Version not found in" in r.message for r in caplog.records)

def test_version_check_package_not_found(tmp_path, caplog):
    """Test VersionChecker when __version__ is missing in __init__.py."""
    caplog.set_level(logging.INFO)
    (tmp_path / "pyproject.toml").write_text("[tool.poetry]\nname = \"compose-to-quadlet\"\nversion = \"0.1.0\"")
    (tmp_path / "__init__.py").write_text("") # Missing __version__
    (tmp_path / "README.md").write_text("# compose-to-quadlet\n\ncompose-to-quadlet v0.1.0")

    runner = CliRunner()
    result = runner.invoke(main, [
        "version-check",
        "--pyproject", str(tmp_path / "pyproject.toml"),
        "--package", str(tmp_path / "__init__.py"),
        "--readme", str(tmp_path / "README.md"),
    ])
    assert result.exit_code != 0
    assert any(r.levelname == "ERROR" and "Version check failed: __version__ not found in" in r.message for r in caplog.records)

def test_version_check_readme_version_mismatch(tmp_path, caplog):
    """Test VersionChecker when README.md version mismatches other files."""
    caplog.set_level(logging.INFO)
    (tmp_path / "pyproject.toml").write_text("[tool.poetry]\nname = \"compose-to-quadlet\"\nversion = \"0.1.0\"")
    (tmp_path / "__init__.py").write_text("__version__ = \"0.1.0\"")
    (tmp_path / "README.md").write_text("# compose-to-quadlet\n\ncompose-to-quadlet v0.1.1") # Mismatch

    runner = CliRunner()
    result = runner.invoke(main, [
        "version-check",
        "--pyproject", str(tmp_path / "pyproject.toml"),
        "--package", str(tmp_path / "__init__.py"),
        "--readme", str(tmp_path / "README.md"),
    ])
    assert result.exit_code != 0
    assert any(r.levelname == "ERROR" and "Version check failed: Version mismatch: README=0.1.1 pyproject=0.1.0 package=0.1.0" in r.message for r in caplog.records)

def test_version_check_pyproject_package_mismatch(tmp_path, caplog):
    """Test VersionChecker when pyproject.toml and package __version__ mismatch."""
    caplog.set_level(logging.INFO)
    (tmp_path / "pyproject.toml").write_text("[tool.poetry]\nname = \"compose-to-quadlet\"\nversion = \"0.1.0\"")
    (tmp_path / "__init__.py").write_text("__version__ = \"0.1.1\"") # Mismatch
    (tmp_path / "README.md").write_text("# compose-to-quadlet\n\ncompose-to-quadlet v0.1.0")

    runner = CliRunner()
    result = runner.invoke(main, [
        "version-check",
        "--pyproject", str(tmp_path / "pyproject.toml"),
        "--package", str(tmp_path / "__init__.py"),
        "--readme", str(tmp_path / "README.md"),
    ])
    assert result.exit_code != 0
    assert any(r.levelname == "ERROR" and "Version check failed: Version mismatch: README=0.1.0 pyproject=0.1.0 package=0.1.1" in r.message for r in caplog.records)

def test_convert_cmd_unexpected_error(tmp_path, caplog):
    """Test the convert command with an unexpected error."""
    caplog.set_level(logging.ERROR)
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text("services:\n  web:\n    image: nginx")

    with patch("compose_to_quadlet.cli.parse_compose_yaml", side_effect=Exception("Unexpected error")):
        runner = CliRunner()
        result = runner.invoke(main, ["convert", str(compose_file)])
        assert result.exit_code != 0
        assert any(r.levelname == "ERROR" and "Error during conversion: Unexpected error" in r.message for r in caplog.records)

def test_version_check_unexpected_error(tmp_path, caplog):
    """Test the version-check command with an unexpected error."""
    caplog.set_level(logging.ERROR)
    with patch("compose_to_quadlet.cli.VersionChecker.check_versions", side_effect=Exception("Unexpected error")):
        runner = CliRunner()
        result = runner.invoke(main, ["version-check"])
        assert result.exit_code != 0
        assert any(r.levelname == "ERROR" and "An unexpected error occurred during version check: Unexpected error" in r.message for r in caplog.records)
