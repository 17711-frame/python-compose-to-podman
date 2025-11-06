# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from compose_to_quadlet.compose_parser import parse_compose_yaml

def test_networks_parsing_map_and_list():
    yml = 'services: { a: { networks: { net1: {} } }, b: { networks: [net2] } }\nnetworks: { net1: {}, net2: {} }'
    spec = parse_compose_yaml(yml)
    assert "net1" in spec.networks and "net2" in spec.networks
    assert spec.services["a"].networks == ["net1"]
    assert spec.services["b"].networks == ["net2"]