import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urdfz.__main__ import pack


def test_pack_robot_urdf_creates_correct_urdfz_file():
    """Test that running pack on robot.urdf creates a properly named .urdfz file."""
    robot_urdf_path = Path(__file__).parent / "assets" / "robot.urdf"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        # Copy the robot.urdf to the temp directory
        test_urdf_path = temp_dir / "robot.urdf"
        _ = test_urdf_path.write_text(robot_urdf_path.read_text())

        # Call the pack function directly
        pack(test_urdf_path)

        # Verify the .urdfz file was created with correct name
        urdfz_path = temp_dir / "robot.urdfz"
        assert urdfz_path.exists(), "The robot.urdfz file should be created"
        assert urdfz_path.suffix == ".urdfz", "The file should have .urdfz extension"


def test_urdfz_file_contains_right_assets_when_unzipped():
    """Test that the .urdfz file contains the right assets when unzipped."""
    robot_urdf_path = Path(__file__).parent / "assets" / "robot.urdf"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        # Copy the robot.urdf to the temp directory
        test_urdf_path = temp_dir / "robot.urdf"
        _ = test_urdf_path.write_text(robot_urdf_path.read_text())

        # Call the pack function directly
        pack(test_urdf_path)

        # Introspect the .urdfz file contents without extracting
        urdfz_path = temp_dir / "robot.urdfz"

        with zipfile.ZipFile(urdfz_path, "r") as zip_file:
            file_list = zip_file.namelist()

            # Verify the URDF file is present
            assert "robot.urdf" in file_list, "Archive should contain robot.urdf"

            # Read and verify URDF content has been modified to use urdfz:// URIs
            urdf_content = zip_file.read("robot.urdf").decode("utf-8")
            assert "urdfz://" in urdf_content, "URDF should contain urdfz:// URIs"
            assert "package://" not in urdf_content, (
                "URDF should not contain original package:// URIs"
            )

            # Verify the URDF is still valid XML with correct structure
            root = ET.fromstring(urdf_content)
            assert root.tag == "robot", "Root element should be 'robot'"
            assert root.get("name") == "test_robot", "Robot name should be preserved"

            # Verify mesh elements have been converted
            mesh_elements = root.findall(".//mesh")
            assert len(mesh_elements) > 0, "Should have mesh elements"

            for mesh in mesh_elements:
                filename = mesh.get("filename", "")
                assert filename.startswith("urdfz://"), (
                    f"Mesh filename should start with urdfz://, got: {filename}"
                )

            # Check for mesh asset files in the archive (if they could be resolved)
            mesh_files = [
                f
                for f in file_list
                if f.endswith(".stl") or f.endswith(".dae") or f.endswith(".obj")
            ]
            if mesh_files:
                # If mesh files are present, verify they're in the expected directory structure
                expected_pattern = "turtlebot3_description/"
                mesh_in_correct_location = any(
                    expected_pattern in mesh_file for mesh_file in mesh_files
                )
                assert mesh_in_correct_location, (
                    f"Mesh files should be in correct directory: {mesh_files}"
                )
