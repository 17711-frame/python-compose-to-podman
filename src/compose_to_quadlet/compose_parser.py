# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from __future__ import annotations
from typing import Any, Dict, List, Union
import yaml
import logging
from .types import ComposeSpec, Service, PortMapping, VolumeMapping, Network, Volume
from .exceptions import ComposeParsingError # Import custom exception

logger = logging.getLogger(__name__)

def _parse_port(port_data: Union[int, str, Dict[str, Any]]) -> PortMapping:
    """Parses a single port mapping entry from a Compose file.

    Args:
        port_data: The raw port data, which can be an int, string, or dictionary.

    Returns:
        A PortMapping object.

    Raises:
        ComposeParsingError: If the port format is unsupported.
    """
    logger.debug(f"Parsing port data: {port_data!r}")
    try:
        if isinstance(port_data, int):
            return PortMapping(host=port_data, container=port_data)
        if isinstance(port_data, str):
            proto = "tcp"
            if "/" in port_data:
                port_data, proto = port_data.split("/", 1)
            host, container = port_data.split(":", 1) if ":" in port_data else (port_data, port_data)
            return PortMapping(host=int(host), container=int(container), protocol=proto)
        if isinstance(port_data, dict):
            return PortMapping(host=int(port_data.get("published", port_data.get("host", port_data.get("target", 0)))),
                               container=int(port_data.get("target", port_data.get("container", 0))),
                               protocol=port_data.get("protocol", "tcp"))
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid port format: {port_data!r} ({e})")
        raise ComposeParsingError(f"Invalid port format: {port_data!r}") from e
    logger.error(f"Unsupported port format encountered: {port_data!r}")
    raise ComposeParsingError(f"Unsupported port format: {port_data!r}")

def _parse_volume(volume_data: Union[str, Dict[str, Any]]) -> VolumeMapping:
    """Parses a single volume mapping entry from a Compose file.

    Args:
        volume_data: The raw volume data, which can be a string or dictionary.

    Returns:
        A VolumeMapping object.

    Raises:
        ComposeParsingError: If the volume format is unsupported.
    """
    logger.debug(f"Parsing volume data: {volume_data!r}")
    if isinstance(volume_data, str):
        parts = volume_data.split(":")
        if len(parts) == 1:
            return VolumeMapping(source=parts[0], target=parts[0])
        if len(parts) >= 2:
            read_only = len(parts) > 2 and "ro" in parts[2]
            return VolumeMapping(source=parts[0], target=parts[1], read_only=read_only)
    if isinstance(volume_data, dict):
        if "target" not in volume_data:
            raise ComposeParsingError(f"Volume dictionary missing 'target': {volume_data!r}")
        return VolumeMapping(source=str(volume_data.get("source", volume_data.get("type","vol"))),
                             target=str(volume_data.get("target", volume_data.get("destination", ""))),
                             read_only=bool(volume_data.get("read_only", False)))
    logger.error(f"Unsupported volume format encountered: {volume_data!r}")
    raise ComposeParsingError(f"Unsupported volume format: {volume_data!r}")

def parse_compose_yaml(text: str) -> ComposeSpec:
    """Parses a Docker Compose YAML string into a ComposeSpec object.

    Args:
        text: The YAML content of the Docker Compose file as a string.

    Returns:
        A ComposeSpec object representing the parsed Compose file.
    """
    logger.info("Starting YAML parsing...")
    data = yaml.safe_load(text) or {}
    services: Dict[str, Service] = {}
    for name, svc_data in (data.get("services") or {}).items():
        logger.debug(f"Parsing service: {name}")
        ports = [ _parse_port(p) for p in (svc_data.get("ports") or []) ]
        env: Dict[str, str] = {}
        environment_data = svc_data.get("environment")
        if isinstance(environment_data, dict):
            env = { str(k): "" if v is None else str(v) for k, v in environment_data.items() }
        elif isinstance(environment_data, list):
            for item in environment_data:
                if isinstance(item, str):
                    if "=" in item:
                        k, v = item.split("=", 1)
                        env[k] = v
                    else:
                        env[item] = ""
        volumes = [ _parse_volume(v) for v in (svc_data.get("volumes") or []) ]
        networks = list((svc_data.get("networks") or {}).keys()) if isinstance(svc_data.get("networks"), dict) else list(svc_data.get("networks") or [])
        depends = list(svc_data.get("depends_on") or [])
        services[name] = Service(
            name=name,
            image=svc_data.get("image"),
            command=svc_data.get("command"),
            environment=env,
            ports=ports,
            volumes=volumes,
            networks=networks,
            depends_on=depends,
            restart=svc_data.get("restart")
        )

    networks_spec: Dict[str, Network] = {}
    for n, ndef in (data.get("networks") or {}).items():
        logger.debug(f"Parsing network: {n}")
        ndef_data = ndef or {} # Ensure ndef is a dict
        networks_spec[n] = Network(name=n, driver=ndef_data.get("driver"), external=bool(ndef_data.get("external", False)))

    volumes_spec: Dict[str, Volume] = {}
    for v, vdef in (data.get("volumes") or {}).items():
        logger.debug(f"Parsing volume: {v}")
        vdef_data = vdef or {} # Ensure vdef is a dict
        volumes_spec[v] = Volume(name=v, external=bool(vdef_data.get("external", False)))

    logger.info("YAML parsing complete.")
    return ComposeSpec(services=services, networks=networks_spec, volumes=volumes_spec)