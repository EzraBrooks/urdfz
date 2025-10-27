from urdfz.pack import remap_filename_to_relative
from urdfz.urdf_utils import read_file_to_str
from unittest.mock import patch, mock_open
from pathlib import Path


def test_read_file_to_str():
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:  # pyright: ignore[reportAny]
        assert read_file_to_str("path/to/my/file") == "data"
        mock_file.assert_called_with("path/to/my/file", "r")  # pyright: ignore[reportAny]
    with patch("builtins.open", mock_open(read_data="data2")) as mock_file:  # pyright: ignore[reportAny]
        path = Path("path/to/my/file2")
        assert read_file_to_str(path) == "data2"
        mock_file.assert_called_with(path, "r")  # pyright: ignore[reportAny]


def test_remap_filename_to_relative():
    assert (
        remap_filename_to_relative("package://ur_description/meshes/link1.stl")
        == Path("ur_description") / "meshes" / "link1.stl"
    )
    assert (
        remap_filename_to_relative(
            "file:///some/weird/place/on/my/disk/robot/link2.stl"
        )
        == Path("robot") / "link2.stl"
    )
