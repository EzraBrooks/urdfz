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

## Features

- **Self-contained**: All mesh files and assets are bundled into a single archive
- **Portable**: No external dependencies needed to view the contents (it's just a ZIP file)
- **ROS Compatible**: Handles `package://` URIs when ROS is available
- **File URI Support**: Also handles `file://` URIs
- **Preserves Structure**: Maintains relative paths within the archive

## URI Support

- `package://package_name/path/to/mesh.dae` - Requires ROS environment (you'll be prompted if missing)
- `file:///absolute/path/to/mesh.dae` - Works anywhere
- Relative paths are resolved relative to the URDF file location

## Requirements

- Python 3.8+
- `typer` for CLI interface

## License

MIT License - see LICENSE file for details.
