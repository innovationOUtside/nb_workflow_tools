# # Simple Routine to remove cells with a particular tag
# either throughout or just at end of notebook
import os
from tm351_nb_utils import exclude_hidden_items

import click
import os

import nbformat
from pathlib import Path


def _process(p, cell_typs, tags):
    """Remove tagged cells."""

    def is_tagged(cell, cell_typs, tags):
        """Return True if cell is correct type and contains a tag in tags."""
        if cell["cell_type"] not in cell_typs:
            return False
        if "metadata" in cell and "tags" in cell["metadata"]:
            return bool(set(cell["metadata"]["tags"]) & set(tags))
        return False
    
    if p.is_file() and p.suffix == ".ipynb":
        # Read notebook
        with p.open("r") as f:
            nb = nbformat.read(f, nbformat.NO_CONVERT)
            cell_count = len(nb.cells)
            nb.cells = [cell for cell in nb.cells if not is_tagged(cell, cell_typs, tags)]

        if cell_count != len(nb.cells):
            print(f"Updating {p}")
            # By default, we do not convert notebook version
            nbformat.write(nb, p.open("w"), nbformat.NO_CONVERT)


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(resolve_path=False))
@click.option(
    "--recursive/--no-recursive", default=True, help="Recursive search of directories."
)
@click.option(
    "--blitz/--no-blitz",
    default=True,
    help="Review all cell types (false if any explicit cell types are set)",
)
@click.option(
    "--code/--no-code",
    default=False,
    help="Check code cell.",
)
@click.option(
    "--md/--no-md",
    default=False,
    help="Check markdown cell.",
)
@click.option(
    "--raw/--no-raw",
    default=False,
    help="Check raw cell.",
)
@click.option(
    "--tag",
    "-t",
    multiple=True,
    help="Specify tags. You can use this option multiple times.",
)
def remove_tagged_cell(paths, recursive, blitz, code, md, raw, tag):
    """Clean empty cells."""
    cell_typs = set()
    tags = list(tag)
    if not tags:
        print("You must enter one or more `-t mytag` arguments")
        return
    if blitz:
        cell_typs = {"code", "markdown", "raw"}
    if code:
        cell_typs.add("code")
    if md:
        cell_typs.add("markdown")
    if raw:
        cell_typs.add("raw")
    for path in paths:
        # Parse notebooks
        nb_dir = Path(path)
        if nb_dir.is_file():
            _process(nb_dir, cell_typs, tags)
        elif recursive:
            exclude = set([])
            for dirname, subdirs, files in os.walk(path, topdown=True):
                subdirs[:] = [d for d in subdirs if d not in exclude]
                exclude_hidden_items(subdirs)
                for p in files:
                    _process(Path(dirname) / p, cell_typs, tags)
        else:
            for p in nb_dir.iterdir():
                _process(p, cell_typs, tags)
