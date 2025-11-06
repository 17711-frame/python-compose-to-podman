# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from compose_to_quadlet.compose_parser import parse_compose_yaml
from compose_to_quadlet.quadlet_writer import write_quadlets
from unittest.mock import patch, MagicMock, mock_open
import os

def test_depends_on_unit_deps(tmp_path):
    yml = 'services: { a: { image: alpine }, b: { image: alpine, depends_on: [a] } }'
    spec = parse_compose_yaml(yml)

    # This mock handles multiple files by returning a different mock object for each path.
    written_content = {}

    def mock_open_side_effect(path, *args, **kwargs):
        handle = MagicMock()
        handle.__enter__.return_value = handle
        handle.write.side_effect = lambda data: written_content.setdefault(path, []).append(data)
        return handle

    with patch("builtins.open", side_effect=mock_open_side_effect):
        write_quadlets(spec, tmp_path.as_posix())

        b_container_path = os.path.join(tmp_path.as_posix(), "b.container")
        b_container_content = "".join(written_content.get(b_container_path, []))

        assert "Wants=a.service" in b_container_content
        assert "After=a.service" in b_container_content