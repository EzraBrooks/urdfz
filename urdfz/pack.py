from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import tempfile
import shutil
import os

from .urdf_utils import read_file_to_str, parse_urdf, get_meshes

try:
    from ament_index_python.packages import get_package_share_directory  # pyright: ignore[reportMissingTypeStubs, reportUnknownVariableType]
except ImportError:

    def get_package_share_directory(package_name: str) -> str:
        raise ImportError(
            f"Cannot resolve 'package://{package_name}' URI - ament_index_python not available. To use package:// URIs, install ROS 2 and source the setup script, or use conda/mamba with robostack."
        )


def make_urdfz_file(urdf_path: str):
    urdf = parse_urdf(read_file_to_str(urdf_path))
    meshes = get_meshes(urdf)
    with tempfile.TemporaryDirectory() as staging_directory:
        staging_directory = Path(staging_directory)
        copy_assets_to_staging_directory(get_mesh_filenames(meshes), staging_directory)
        rewrite_mesh_filenames(meshes)
        ET.ElementTree(urdf).write(staging_directory / Path(urdf_path).name)
        # Create a second temporary directory to hold the archive while it's still a ".zip" file before it gets renamed to ".urdfz" so we don't confuse ourselves by putting files into the directory we're compressing
        with tempfile.TemporaryDirectory() as archive_temporary_directory:
            archive_temporary_directory = Path(archive_temporary_directory)
            _ = shutil.move(
                shutil.make_archive(
                    str(archive_temporary_directory / "urdfz"),
                    "zip",
                    staging_directory,
                ),
                "test.urdfz",
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
