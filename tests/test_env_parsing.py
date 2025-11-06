# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from compose_to_quadlet.compose_parser import parse_compose_yaml

def test_environment_list_and_dict():
    yml = 'services: { a: { environment: ["A=1"], }, b: { environment: { B: 2 } } }'
    spec = parse_compose_yaml(yml)
    assert spec.services["a"].environment["A"] == "1"
    assert spec.services["b"].environment["B"] == "2"

def test_environment_valueless():
    yml = 'services: { a: { environment: ["A", "B="] } }'
    spec = parse_compose_yaml(yml)
    assert "A" in spec.services["a"].environment and spec.services["a"].environment["A"] == ""
    assert "B" in spec.services["a"].environment and spec.services["a"].environment["B"] == ""
