# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from __future__ import annotations
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field

class PortMapping(BaseModel):
    """Represents a port mapping from host to container."""
    host: int = Field(..., description="The host port.")
    container: int = Field(..., description="The container port.")
    protocol: str = Field("tcp", description="The protocol (e.g., 'tcp', 'udp').")

class VolumeMapping(BaseModel):
    """Represents a volume mapping from source to target."""
    source: str = Field(..., description="The source path or volume name.")
    target: str = Field(..., description="The target path in the container.")
    read_only: bool = Field(False, description="Whether the volume is read-only.")

class Service(BaseModel):
    """Represents a Docker Compose service."""
    name: str = Field(..., description="The name of the service.")
    image: Optional[str] = Field(None, description="The container image to use.")
    command: Optional[Union[str, List[str]]] = Field(None, description="The command to execute in the container.")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment variables for the service.")
    ports: List[PortMapping] = Field(default_factory=list, description="List of port mappings.")
    volumes: List[VolumeMapping] = Field(default_factory=list, description="List of volume mappings.")
    networks: List[str] = Field(default_factory=list, description="List of networks the service connects to.")
    depends_on: List[str] = Field(default_factory=list, description="List of services this service depends on.")
    restart: Optional[str] = Field(None, description="Restart policy for the service (e.g., 'always', 'on-failure').")

class Network(BaseModel):
    """Represents a Docker Compose network."""
    name: str = Field(..., description="The name of the network.")
    driver: Optional[str] = Field(None, description="The network driver to use.")
    external: bool = Field(False, description="Whether the network is external.")

class Volume(BaseModel):
    """Represents a Docker Compose volume."""
    name: str = Field(..., description="The name of the volume.")
    external: bool = Field(False, description="Whether the volume is external.")

class ComposeSpec(BaseModel):
    """Represents the parsed Docker Compose specification."""
    services: Dict[str, Service] = Field(default_factory=dict, description="Dictionary of services defined in the Compose file.")
    networks: Dict[str, Network] = Field(default_factory=dict, description="Dictionary of networks defined in the Compose file.")
    volumes: Dict[str, Volume] = Field(default_factory=dict, description="Dictionary of volumes defined in the Compose file.")