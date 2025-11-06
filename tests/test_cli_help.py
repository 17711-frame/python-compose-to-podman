# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
import subprocess, sys, os, json, pathlib

def test_cli_help_runs(tmp_path):
    # Ensure CLI module imports and --help works
    import compose_to_quadlet.cli as cli  # noqa: F401