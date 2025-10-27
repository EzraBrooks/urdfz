from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import tempfile
import shutil
from ament_index_python.packages import get_package_share_directory
import os

ET.register_namespace("", "http://www.ros.org")


def make_urdfz_file(urdf_path: str):
    urdf = parse_urdf(read_file_to_str(urdf_path))
    meshes = get_meshes(urdf)
    with tempfile.TemporaryDirectory() as staging_directory:
        copy_assets_to_staging_directory(
            get_mesh_filenames(meshes), Path(staging_directory)
        )
        rewrite_mesh_filenames(meshes)
        ET.ElementTree(urdf).write(Path(staging_directory) / Path(urdf_path).name)
        _ = shutil.move(
            shutil.make_archive("test", "zip", Path(staging_directory)), "test.urdfz"
        )


def copy_assets_to_staging_directory(paths: list[str], staging_directory: Path):
    for path in paths:
        new_path = staging_directory / remap_filename_to_relative(path)
        if not new_path.parent.exists():
            os.makedirs(new_path.parent)
        _ = shutil.copy(
            get_path_to_file(path),
            new_path,
        )


def read_file_to_str(path: Path | str) -> str:
    with open(path, "r") as f:
        return f.read()


def parse_urdf(raw_urdf: str) -> ET.Element:
    return ET.fromstring(raw_urdf)


def get_meshes(urdf: ET.Element) -> list[ET.Element]:
    # A little ugly but it was a quick way to support URDFs that (correctly?) contain the ROS.org namespace and also ones that don't.
    # Maybe we should validate and be opinionated though ;)
    return urdf.findall(
        ".//mesh", namespaces={"": "http://www.ros.org"}
    ) + urdf.findall(".//mesh")


def get_mesh_filenames(meshes: list[ET.Element]) -> list[str]:
    """Extract the `filename` attribute of all mesh elements"""
    return [mesh.attrib["filename"] for mesh in meshes]


def rewrite_mesh_filenames(meshes: list[ET.Element]):
    for mesh in meshes:
        mesh.attrib["filename"] = "urdfz://" + str(
            remap_filename_to_relative(mesh.attrib["filename"])
        )


def get_path_to_file(filename: str) -> Path:
    url = urlparse(filename)
    if url.scheme == "package":
        return Path(get_package_share_directory(url.netloc)) / f".{url.path}"
    elif url.scheme == "file":
        return Path(url.netloc) / url.path
    else:
        raise NotImplementedError(
            f"Found unsupported URDF filename URI scheme {url.scheme}!"
        )


def remap_filename_to_relative(filename: str) -> Path:
    """Generate the relative file:// URI to be used inside the URDFZ archive
    from a file:// or package:// URI in the original URDF"""
    url = urlparse(filename)
    # If it's a ROS package URL, just use the entire path as our relative
    # namespace inside the resulting URDFZ
    if url.scheme == "package":
        return Path(url.netloc) / f".{url.path}"
    # If it's a file path, just use the closest directory name as the relative
    # path so we are more likely to be idempotent and less likely to
    # accidentally dump system- or user-identifying information into the
    # archive
    elif url.scheme == "file":
        split_path = url.path.split("/")
        return Path(split_path[-2]) / split_path[-1]
    else:
        raise NotImplementedError(
            f"Found unsupported URDF filename URI scheme {url.scheme}!"
        )
