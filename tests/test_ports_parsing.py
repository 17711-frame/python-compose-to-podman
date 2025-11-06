# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from compose_to_quadlet.compose_parser import parse_compose_yaml
from compose_to_quadlet.exceptions import ComposeParsingError
import pytest

def test_ports_parsing_various_formats():
    yml = '''
services:
  a:
    ports:
      - "8080"
      - "8081:80"
      - "8082:80/udp"
      - target: 8083
        published: 8083
        protocol: tcp
'''
    spec = parse_compose_yaml(yml)
    ports = spec.services["a"].ports
    assert len(ports) == 4
    assert ports[0].host == 8080 and ports[0].container == 8080 and ports[0].protocol == "tcp"
    assert ports[1].host == 8081 and ports[1].container == 80 and ports[1].protocol == "tcp"
    assert ports[2].host == 8082 and ports[2].container == 80 and ports[2].protocol == "udp"
    assert ports[3].host == 8083 and ports[3].container == 8083 and ports[3].protocol == "tcp"

def test_invalid_port_format_raises_error():
    yml = '''
services:
  a:
    ports:
      - "invalid-port"
'''
    with pytest.raises(ComposeParsingError, match="Invalid port format"):
        parse_compose_yaml(yml)
