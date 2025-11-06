# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from compose_to_quadlet.compose_parser import parse_compose_yaml
from compose_to_quadlet.exceptions import ComposeParsingError
import pytest

def test_volume_parsing_various_formats():
    yml = '''
services:
  a:
    volumes:
      - /host/path:/container/path
      - vol_name:/container/path2:ro
      - type: bind
        source: /host/path3
        target: /container/path3
        read_only: true
      - my_named_volume
volumes:
  my_named_volume:
'''
    spec = parse_compose_yaml(yml)
    volumes = spec.services["a"].volumes
    assert len(volumes) == 4
    assert volumes[0].source == "/host/path" and volumes[0].target == "/container/path" and not volumes[0].read_only
    assert volumes[1].source == "vol_name" and volumes[1].target == "/container/path2" and volumes[1].read_only
    assert volumes[2].source == "/host/path3" and volumes[2].target == "/container/path3" and volumes[2].read_only
    assert volumes[3].source == "my_named_volume" and volumes[3].target == "my_named_volume" and not volumes[3].read_only

def test_volume_parsing_named_volume_only():
    yml = '''
services:
  a:
    volumes:
      - my_named_volume
volumes:
  my_named_volume:
'''
    spec = parse_compose_yaml(yml)
    volumes = spec.services["a"].volumes
    assert len(volumes) == 1
    assert volumes[0].source == "my_named_volume" and volumes[0].target == "my_named_volume"

def test_invalid_volume_format_raises_error():
    yml = '''
services:
  a:
    volumes:
      - { source: /path, readonly: true }
'''
    with pytest.raises(ComposeParsingError, match="Volume dictionary missing 'target'"):
        parse_compose_yaml(yml)

def test_volume_parsing_extra_parts():
    yml = '''
services:
  a:
    volumes:
      - /host/path:/container/path:ro:extra
'''
    spec = parse_compose_yaml(yml)
    volumes = spec.services["a"].volumes
    assert len(volumes) == 1
    assert volumes[0].source == "/host/path" and volumes[0].target == "/container/path" and volumes[0].read_only