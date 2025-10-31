from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import tempfile
import shutil
import os

from resolve_robotics_uri_py import resolve_robotics_uri  # pyright: ignore[reportMissingTypeStubs]

from .urdf_utils import read_file_to_str, parse_urdf, get_meshes


def make_urdfz_file(urdf_path: Path):
    urdf = parse_urdf(read_file_to_str(urdf_path))
    meshes = get_meshes(urdf)
    with tempfile.TemporaryDirectory() as staging_directory:
        staging_directory = Path(staging_directory)
        copy_assets_to_staging_directory(
            get_mesh_filenames(meshes), staging_directory, urdf_path
        )
        rewrite_mesh_filenames(meshes, urdf_path)
        ET.ElementTree(urdf).write(staging_directory / urdf_path.name)
        # Create a second temporary directory to hold the archive while it's still a ".zip" file before it gets renamed to ".urdfz" so we don't confuse ourselves by putting files into the directory we're compressing
        with tempfile.TemporaryDirectory() as archive_temporary_directory:
            archive_temporary_directory = Path(archive_temporary_directory)
            _ = shutil.move(
                shutil.make_archive(
                    str(archive_temporary_directory / "urdfz"),
                    "zip",
                    staging_directory,
                ),
                urdf_path.with_suffix(".urdfz"),
            )


def copy_assets_to_staging_directory(
    paths: list[str], staging_directory: Path, urdf_path: Path
):
    for path in paths:
        new_path = staging_directory / remap_filename_to_relative(path, urdf_path)
        if not new_path.parent.exists():
            os.makedirs(new_path.parent)
        _ = shutil.copy(
            resolve_robotics_uri(path),
            new_path,
        )


def get_mesh_filenames(meshes: list[ET.Element]) -> list[str]:
    """Extract the `filename` attribute of all mesh elements"""
    return [mesh.attrib["filename"] for mesh in meshes]


def rewrite_mesh_filenames(meshes: list[ET.Element], urdf_path: Path):
    for mesh in meshes:
        mesh.attrib["filename"] = create_urdfz_uri(mesh.attrib["filename"], urdf_path)


def create_urdfz_uri(filename: str, urdf_path: Path):
    return "urdfz://" + remap_filename_to_relative(filename, urdf_path).as_posix()


def remap_filename_to_relative(filename: str, urdf_path: Path) -> Path:
    """Generate the relative file:// URI to be used inside the URDFZ archive
    from a file:// or package:// URI in the original URDF"""
    url = urlparse(filename)
    # If it's a ROS package URL, just use the entire path as our relative
    # namespace inside the resulting URDFZ
    if url.scheme == "package":
        return Path(url.netloc) / f".{url.path}"
    elif url.scheme == "file":
        url_path = Path(url.path)
        # Maintain relative paths below the URDF file, to preserve URDFZ idempotence
        # All the "resolve" shenanigans here are to handle symlinks (for example tempdirs on macOS in /var/)
        if url_path.resolve().is_relative_to(urdf_path.parent.resolve()):
            return url_path.resolve().relative_to(urdf_path.parent.resolve())
        # Otherwise squash the URL to only one folder deep to avoid accidental
        # inclusion of system- or user-identifying information
        else:
            return url_path.resolve().relative_to(url_path.parent.parent.resolve())
    else:
        raise NotImplementedError(
            f"Found unsupported URDF filename URI scheme {url.scheme}!"
        )
