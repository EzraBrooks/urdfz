# urdfz

Self-contained, portable, actually UNIFIED Robot Description Files (URDFs)

A CLI tool for creating and unpacking URDFZ archives that contain URDFs and all their associated mesh files and assets in a single portable archive.

## Installation

```bash
pip install urdfz
```

## Usage

### Pack a URDF into a URDFZ archive

```bash
urdfz pack path/to/your/robot.urdf
```

This will create a `robot.urdfz` file containing the URDF and all referenced mesh files.

### Unpack a URDFZ archive

```bash
urdfz unpack path/to/robot.urdfz
```

This will extract the URDF and all mesh files to the current directory.

## Things URDFZ aims to support

- All of the actual URDF standard as written.

## Things URDFZ will probably never support

- xacro. it's not called xacroZ. To me it seems obvious that if you want to freeze your URDF in time, you should do it *after* generating it from xacro.
  - This includes find-package expressions! We already have `package://`!

## Requirements

- Python 3.8+
- `typer` for CLI interface

## License

MIT License - see LICENSE file for details.
