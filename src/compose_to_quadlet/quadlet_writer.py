# Part of the project compose-to-quadlet — Licensed under MIT © The 17711 Frame (https://17711.org)
from __future__ import annotations
from typing import Iterable, List, Tuple, Optional, Union
from .types import ComposeSpec, Service, PortMapping, VolumeMapping, Network, Volume
import os
import logging

logger = logging.getLogger(__name__)

def _unit_header(name: str, wants: Optional[List[str]] = None, after: Optional[List[str]] = None) -> str:
    """Generates the [Unit] section of a Quadlet unit file.

    Args:
        name: The name of the service/unit.
        wants: A list of unit names that this unit desires to start.
        after: A list of unit names that this unit should start after.

    Returns:
        A string representing the [Unit] section.
    """
    logger.debug(f"Generating unit header for {name}")
    wants = wants or []
    after = after or []
    lines = ["[Unit]"]
    if wants: lines.append(f"Wants={' '.join(wants)}")
    if after: lines.append(f"After={' '.join(after)}")
    return "\n".join(lines)

def _container_section(svc: Service) -> str:
    """Generates the [Container] section for a Quadlet container unit file.

    Args:
        svc: The Service object containing container configuration.

    Returns:
        A string representing the [Container] section.
    """
    logger.debug(f"Generating container section for service: {svc.name}")
    lines = ["[Container]"]
    if svc.image:
        lines.append(f"Image={svc.image}")
    if svc.command:
        if isinstance(svc.command, list):
            lines.append("Exec=" + " ".join(str(x) for x in svc.command))
        else:
            lines.append(f"Exec={svc.command}")
    for k, v in svc.environment.items():
        lines.append(f"Environment={k}={v}")
    for p in svc.ports:
        port = f"{p.host}:{p.container}"
        if p.protocol and p.protocol != "tcp":
            port += f"/{p.protocol}"
        lines.append(f"PublishPort={port}")
    for v in svc.volumes:
        vol = f"{v.source}:{v.target}"
        if v.read_only:
            vol += ":ro"
        lines.append(f"Volume={vol}")
    if svc.restart:
        # Map basic policies: always, on-failure, unless-stopped
        policy = "on-failure"
        if svc.restart in ["always", "unless-stopped"]:
            policy = "always"
        lines.append(f"RestartPolicy={policy}")
    for net in svc.networks:
        lines.append(f"Network={net}")
    return "\n".join(lines)

def _install_section() -> str:
    """Generates the [Install] section for a Quadlet unit file.

    Returns:
        A string representing the [Install] section.
    """
    logger.debug("Generating install section")
    return "\n".join([
        "[Install]",
        "WantedBy=default.target"
    ])

def service_dependencies(svc: Service) -> Tuple[List[str], List[str]]:
    """Determines the 'Wants' and 'After' dependencies for a service.

    Args:
        svc: The Service object.

    Returns:
        A tuple containing two lists: (wants_list, after_list).
    """
    logger.debug(f"Determining dependencies for service: {svc.name}")
    wants = [f"{dep}.service" for dep in svc.depends_on]
    after = wants[:]
    return wants, after

def write_quadlets(spec: ComposeSpec, outdir: str) -> List[str]:
    """Writes Quadlet unit files based on the parsed Compose specification.

    Args:
        spec: The ComposeSpec object containing services, networks, and volumes.
        outdir: The output directory where Quadlet files will be written.

    Returns:
        A list of absolute paths to the written Quadlet files.
    """
    logger.info(f"Writing Quadlet files to directory: {outdir}")
    os.makedirs(outdir, exist_ok=True)
    written_files: List[str] = []

    # Networks
    for n in spec.networks.values():
        if n.external:
            logger.debug(f"Skipping external network: {n.name}")
            continue
        path = os.path.join(outdir, f"{n.name}.network")
        content = "\n".join([
            "[Network]",
            f"Name={n.name}"
        ])
        with open(path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        written_files.append(path)
        logger.debug(f"Wrote network file: {path}")

    # Volumes
    for v in spec.volumes.values():
        if v.external:
            logger.debug(f"Skipping external volume: {v.name}")
            continue
        path = os.path.join(outdir, f"{v.name}.volume")
        content = "\n".join([
            "[Volume]",
            f"VolumeName={v.name}"
        ])
        with open(path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        written_files.append(path)
        logger.debug(f"Wrote volume file: {path}")

    # Services/Containers
    for svc in spec.services.values():
        wants, after = service_dependencies(svc)
        path = os.path.join(outdir, f"{svc.name}.container")
        content = "\n\n".join([
            _unit_header(svc.name, wants=wants, after=after),
            _container_section(svc),
            _install_section(),
        ])
        with open(path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        written_files.append(path)
        logger.debug(f"Wrote container file: {path}")

    logger.info(f"Successfully wrote {len(written_files)} Quadlet files.")
    return written_files