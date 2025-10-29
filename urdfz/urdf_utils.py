from pathlib import Path
import xml.etree.ElementTree as ET

ET.register_namespace("", "http://www.ros.org")


def read_file_to_str(path: Path) -> str:
    """Read a file and return its contents as a string"""
    with open(path, "r") as f:
        return f.read()


def parse_urdf(raw_urdf: str) -> ET.Element:
    """Parse a URDF string into an XML Element"""
    return ET.fromstring(raw_urdf)


def get_meshes(urdf: ET.Element) -> list[ET.Element]:
    """Extract all mesh elements from a URDF Element

    A little ugly but it was a quick way to support URDFs that (correctly?)
    contain the ROS.org namespace and also ones that don't.
    Maybe we should validate and be opinionated though ;)
    """
    return urdf.findall(
        ".//mesh", namespaces={"": "http://www.ros.org"}
    ) + urdf.findall(".//mesh")
