from pathlib import Path


def read_file_to_str(path: Path | str) -> str:
    with open(path, "r") as f:
        return f.read()
