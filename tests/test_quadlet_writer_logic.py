# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from compose_to_quadlet.quadlet_writer import _container_section, _unit_header
from compose_to_quadlet.types import Service, PortMapping

def test_unit_header_no_deps():
    """Test _unit_header with no dependencies."""
    header = _unit_header("test_svc")
    assert "Wants=" not in header
    assert "After=" not in header

def test_container_section_no_image():
    """Test _container_section for a service with no image."""
    svc = Service(name="test_svc")
    section = _container_section(svc)
    assert "Image=" not in section

def test_container_section_string_command():
    """Test _container_section for a service with a string command."""
    svc = Service(name="test_svc", command="echo hello")
    section = _container_section(svc)
    assert "Exec=echo hello" in section

def test_container_section_tcp_protocol():
    """Test _container_section with a TCP port mapping."""
    svc = Service(name="test_svc", ports=[PortMapping(host=80, container=80, protocol="tcp")])
    section = _container_section(svc)
    assert "PublishPort=80:80" in section
    assert "80:80/tcp" not in section
