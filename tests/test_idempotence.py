import tempfile
from pathlib import Path
from urdfz.pack import make_urdfz_file
from urdfz.unpack import unpack_urdfz_file
from urdfz.urdf_utils import parse_urdf, read_file_to_str, get_meshes


def test_idempotence():
    """
    Ensure URDFZ is idempotent by ensuring that a pack/unpack/pack/unpack
    cycle produces the same file:// URIs as the original pack/unpack cycle.
    """
    robot_urdf_path = Path(__file__).parent / "assets" / "robot.urdf"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        # Original URDF
        original_urdf_path = temp_dir / "robot.urdf"
        _ = original_urdf_path.write_text(robot_urdf_path.read_text())

        # First pack/unpack cycle
        make_urdfz_file(original_urdf_path)
        first_urdfz_path = temp_dir / "robot.urdfz"

        first_unpack_dir = temp_dir / "first_unpack"
        unpack_urdfz_file(first_urdfz_path, first_unpack_dir)

        # Second pack/unpack cycle
        first_unpacked_urdf = first_unpack_dir / "robot.urdf"
        make_urdfz_file(first_unpacked_urdf)
        second_urdfz_path = first_unpack_dir / "robot.urdfz"

        second_unpack_dir = temp_dir / "second_unpack"
        unpack_urdfz_file(second_urdfz_path, second_unpack_dir)

        # Compare relative path structure - should be identical for idempotent operations
        first_unpacked_content = read_file_to_str(first_unpack_dir / "robot.urdf")
        second_unpacked_content = read_file_to_str(second_unpack_dir / "robot.urdf")

        first_meshes = get_meshes(parse_urdf(first_unpacked_content))
        second_meshes = get_meshes(parse_urdf(second_unpacked_content))

        for i, (first_mesh, second_mesh) in enumerate(zip(first_meshes, second_meshes)):
            first_uri = first_mesh.attrib["filename"]
            second_uri = second_mesh.attrib["filename"]

            # Parse URIs and get the relative path within each unpack directory
            from urllib.parse import urlparse

            first_parsed = urlparse(first_uri)
            second_parsed = urlparse(second_uri)

            first_abs_path = Path(first_parsed.path).resolve()
            second_abs_path = Path(second_parsed.path).resolve()

            # Get relative paths by finding what comes after the unpack directory
            first_unpack_resolved = first_unpack_dir.resolve()
            second_unpack_resolved = second_unpack_dir.resolve()

            first_relative = first_abs_path.relative_to(first_unpack_resolved)
            second_relative = second_abs_path.relative_to(second_unpack_resolved)

            print(f"Mesh {i} relative paths:")
            print(f"  First cycle:  {first_relative}")
            print(f"  Second cycle: {second_relative}")

            assert first_relative == second_relative, (
                f"Pack/unpack operations should be idempotent, but relative paths differ:\n"
                f"First:  {first_relative}\n"
                f"Second: {second_relative}"
            )
