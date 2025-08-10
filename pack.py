from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


def read_file_to_str(path: Path | str) -> str:
    with open(path, "r") as f:
        return f.read()


def parse_urdf(raw_urdf: str) -> ET.Element:
    return ET.fromstring(raw_urdf)


def get_meshes(urdf: ET.Element) -> list[ET.Element]:
    return urdf.findall("mesh")


def get_mesh_filenames(meshes: list[ET.Element]) -> list[str]:
    """Extract the `filename` attribute of all mesh elements"""
    return [mesh.attrib["filename"] for mesh in meshes]


def remap_filename_to_relative(filename: str) -> Path:
    """Generate the relative file:// URI to be used inside the URDFZ archive
    from a file:// or package:// URI in the original URDF"""
    url = urlparse(filename)
    # If it's a ROS package URL, just use the entire path as our relative
    # namespace inside the resulting URDFZ
    if url.scheme == "package":
        return Path.cwd() / url.netloc / f".{url.path}"
    # If it's a file path, just use the closest directory name as the relative
    # path so we are more likely to be idempotent and less likely to
    # accidentally dump system- or user-identifying information into the
    # archive
    elif url.scheme == "file":
        split_path = url.path.split("/")
        return Path.cwd() / split_path[-2] / split_path[-1]
    else:
        raise NotImplementedError(
            f"Found unsupported URDF filename URI scheme {url.scheme}!"
        )
