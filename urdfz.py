import typer
from typing_extensions import Annotated

from pack import make_urdfz_file

cli = typer.Typer()


@cli.command()
def pack(
    path: Annotated[str, typer.Argument(help="The path to the URDF file to pack")],
):
    """Packs a URDF and all its assets into a URDFZ file."""
    make_urdfz_file(path)


@cli.command()
def unpack(
    path: Annotated[str, typer.Argument(help="The path to the URDFZ file to unpack")],  # pyright: ignore[reportUnusedParameter]
):
    """Unpacks a URDFZ into its component URDF file and assets."""
    raise NotImplementedError()


if __name__ == "__main__":
    cli()
