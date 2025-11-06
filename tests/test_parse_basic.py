# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from compose_to_quadlet.compose_parser import parse_compose_yaml, _parse_port, _parse_volume
from compose_to_quadlet.types import PortMapping, VolumeMapping
from compose_to_quadlet.exceptions import ComposeParsingError # Import custom exception
import pytest

def test_parse_basic_service():
    """Test parsing a basic service definition."""
    yml = 'services: { a: { image: alpine, command: ["echo", "hello"] } }'
    spec = parse_compose_yaml(yml)
    assert "a" in spec.services
    assert spec.services["a"].image == "alpine"
    assert spec.services["a"].command == ["echo", "hello"]

def test_parse_port_unsupported_format():
    """Test _parse_port with an unsupported format raises ComposeParsingError."""
    with pytest.raises(ComposeParsingError, match="Unsupported port format"):
        _parse_port(None) # type: ignore

    with pytest.raises(ComposeParsingError, match="Unsupported port format"):
        _parse_port([]) # type: ignore

def test_parse_volume_unsupported_format():
    """Test _parse_volume with an unsupported format raises ComposeParsingError."""
    with pytest.raises(ComposeParsingError, match="Unsupported volume format"):
        _parse_volume(None) # type: ignore

    with pytest.raises(ComposeParsingError, match="Unsupported volume format"):
        _parse_volume(123) # type: ignore

def test_parse_empty_compose_file():
    """Test parsing an empty or null compose file."""
    spec = parse_compose_yaml("")
    assert not spec.services
    assert not spec.networks
    assert not spec.volumes

    spec = parse_compose_yaml("---")
    assert not spec.services
    assert not spec.networks
    assert not spec.volumes

def test_parse_compose_file_no_services():
    """Test parsing a compose file with no services defined."""
    yml = 'version: "3.8"\nnetworks:\n  default:\n'
    spec = parse_compose_yaml(yml)
    assert not spec.services