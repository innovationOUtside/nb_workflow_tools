# # Simple Routine to remove blank cells,
# either throughout or just at end of notebook
import os
from tm351_nb_utils import exclude_hidden_items

import click
import os

import nbformat
from pathlib import Path

def _process(p, all, cell_typs, stripwhitespace):
    """Clean empty cells."""

    # Function to check if a cell is empty and of an approved type
    def is_empty_approved(cell):
        source = cell.get("source", "")
        # Cope with v4 and v5 notebooks
        if isinstance(source, list):
            source = "".join(source)

        if not stripwhitespace:
            return cell["cell_type"] in cell_typs and not source
        return cell["cell_type"] in cell_typs and not source.strip()

    if p.is_file() and p.suffix == ".ipynb":
        # Read notebook
        with p.open("r") as f:
            nb = nbformat.read(f, nbformat.NO_CONVERT)
            cell_count = len(nb.cells)
            if all:
                nb.cells = [cell for cell in nb.cells if not is_empty_approved(cell)]
            else:
                # Strip empty cells from the start
                while nb.cells and is_empty_approved(nb.cells[0]):
                    nb.cells.pop(0)

                # Strip empty cells from the end
                while nb.cells and is_empty_approved(nb.cells[-1]):
                    nb.cells.pop()

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
    "--all/--no-all",
    default=False,
    help="Remove all empty cells, not just empty initial and final cells.",
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
    "--stripwhitespace/--no-stripwhitespace",
    default=True,
    help="Strip whitespace.",
)
def empty_cell_cleaner(paths, recursive, all, blitz, code, md, raw, stripwhitespace):
    """Clean empty cells."""
    cell_typs = set()
    if blitz:
        cell_typs = {"code", "markdown", "raw"}
    if code or md or raw:
        cell_typs = set()
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
            _process(nb_dir, all, cell_typs, stripwhitespace)
        elif recursive:
            exclude = set([])
            for dirname, subdirs, files in os.walk(path, topdown=True):
                subdirs[:] = [d for d in subdirs if d not in exclude]
                exclude_hidden_items(subdirs)
                for p in files:
                    _process(Path(dirname) / p, all, cell_typs, stripwhitespace)
        else:
            for p in nb_dir.iterdir():
                _process(p, all, cell_typs, stripwhitespace)
