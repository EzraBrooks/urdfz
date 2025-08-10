from pack import read_file_to_str, remap_filename_to_relative
from unittest.mock import patch, mock_open
from pathlib import Path


def test_read_file_to_str():
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        assert read_file_to_str("path/to/my/file") == "data"
        mock_file.assert_called_with("path/to/my/file", "r")
    with patch("builtins.open", mock_open(read_data="data2")) as mock_file:
        path = Path("path/to/my/file2")
        assert read_file_to_str(path) == "data2"
        mock_file.assert_called_with(path, "r")


def test_remap_filename_to_relative():
    assert remap_filename_to_relative("package://ur_description/meshes/link1.stl") == (
        Path.cwd() / "ur_description" / "meshes" / "link1.stl"
    )
    assert (
        remap_filename_to_relative(
            "file:///some/weird/place/on/my/disk/robot/link2.stl"
        )
        == Path.cwd() / "robot" / "link2.stl"
    )
