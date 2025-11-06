# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from compose_to_quadlet.compose_parser import parse_compose_yaml
from compose_to_quadlet.quadlet_writer import write_quadlets
from unittest.mock import patch, MagicMock
import os

def test_restart_policy_mapping(tmp_path):
    yml = '''
services:
  always_svc:
    image: alpine
    restart: always
  on_failure_svc:
    image: alpine
    restart: on-failure
  unless_stopped_svc:
    image: alpine
    restart: unless-stopped
  no_restart_svc:
    image: alpine
'''
    spec = parse_compose_yaml(yml)

    written_content = {}

    def mock_open_side_effect(path, *args, **kwargs):
        handle = MagicMock()
        handle.__enter__.return_value = handle
        handle.write.side_effect = lambda data: written_content.setdefault(path, []).append(data)
        return handle

    with patch("builtins.open", side_effect=mock_open_side_effect):
        write_quadlets(spec, tmp_path.as_posix())

        always_path = os.path.join(tmp_path.as_posix(), "always_svc.container")
        on_failure_path = os.path.join(tmp_path.as_posix(), "on_failure_svc.container")
        unless_stopped_path = os.path.join(tmp_path.as_posix(), "unless_stopped_svc.container")
        no_restart_path = os.path.join(tmp_path.as_posix(), "no_restart_svc.container")

        always_content = "".join(written_content.get(always_path, []))
        on_failure_content = "".join(written_content.get(on_failure_path, []))
        unless_stopped_content = "".join(written_content.get(unless_stopped_path, []))
        no_restart_content = "".join(written_content.get(no_restart_path, []))

        assert "RestartPolicy=always" in always_content
        assert "RestartPolicy=on-failure" in on_failure_content
        assert "RestartPolicy=always" in unless_stopped_content # unless-stopped maps to always
        assert "RestartPolicy" not in no_restart_content