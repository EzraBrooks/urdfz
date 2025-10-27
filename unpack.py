from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import zipfile

from urdf_utils import read_file_to_str, parse_urdf, get_meshes


def unpack_urdfz_file(urdfz_path: str | Path, output_dir: str | Path | None = None):
    """Unpack a URDFZ file to a directory named after the URDFZ file"""
    urdfz_path = Path(urdfz_path)

    # Create output directory based on URDFZ filename if not specified
    if output_dir is None:
        output_dir = Path(urdfz_path.stem)  # Remove .urdfz extension
    else:
        output_dir = Path(output_dir)

    # Create the output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)

    # Extract the URDFZ (zip) file directly to the output directory
    with zipfile.ZipFile(urdfz_path, "r") as zip_ref:
        zip_ref.extractall(output_dir)

    # Find the URDF file in the extracted contents
    urdf_files = list(output_dir.glob("*.urdf"))
    if not urdf_files:
        raise FileNotFoundError("No URDF file found in the URDFZ archive")
    if len(urdf_files) > 1:
        raise ValueError("Multiple URDF files found in the URDFZ archive")

    urdf_file = urdf_files[0]
    urdf = parse_urdf(read_file_to_str(urdf_file))
    meshes = get_meshes(urdf)

    # Rewrite mesh filenames from urdfz:// to file:// URLs
    rewrite_mesh_filenames_to_file_urls(meshes)

    # Write the modified URDF back to the same location
    ET.ElementTree(urdf).write(urdf_file, encoding="utf-8", xml_declaration=True)

    print(f"Unpacked URDFZ to directory: {output_dir}/")


def rewrite_mesh_filenames_to_file_urls(meshes: list[ET.Element]):
    """Convert urdfz:// URLs back to file:// URLs pointing to local files"""
    for mesh in meshes:
        filename = mesh.attrib["filename"]
        url = urlparse(filename)

        if url.scheme == "urdfz":
            relative_path = Path(url.netloc) / url.path[1:]  # Remove leading slash

            # Use as_uri() to properly format the file URI for all platforms
            # Must resolve to absolute path first since relative paths can't be URIs
            mesh.attrib["filename"] = relative_path.resolve().as_uri()
        else:
            raise Exception("All URIs inside a URDFZ file should be in urdfz:// form!")
