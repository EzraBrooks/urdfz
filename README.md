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

## How does it work?

Upon packing, URDFZ treats your URDF as an archive manifest for your URDFZ archive.
It looks up all the URIs listed in the URDF, resolves them to absolute paths, and copies them into the archive.
It then creates a copy of your URDF that has its URIs rewritten to a `urdfz://` scheme that points to the asset's path within the archive, and places that modified URDF at the root of the archive.

Upon unpacking, URDFZ unzips its archive and replaces the `urdfz://` URI scheme with the resulting absolute path on-disk after extraction.
A side effect of this is that `urdfz pack` -> `urdfz unpack` can additionally be used as a way to sever your connection to upstream robot description packages, as the `package://` URLs are currently deliberately not persisted.
If you've ever had an upstream description change break your production robot during a distro upgrade, you know what I'm talking about!



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
