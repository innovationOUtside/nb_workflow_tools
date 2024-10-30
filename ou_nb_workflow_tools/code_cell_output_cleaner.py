# Simple Routine to clean code output cells
# Either all cells, just tagged cells, or not tagged cells
import os
from tm351_nb_utils import exclude_hidden_items

import click
import os

import nbformat
from pathlib import Path


def _process(p, blitz, retain, tags):
    """Clean code cell outputs."""

    def istagged(cell, tags):
        """Identify if cell is tagged for cleaning."""
        if cell.cell_type == "code" and "metadata" in cell and "tags" in cell["metadata"]:
            return bool(set(cell["metadata"]["tags"]) & set(tags))
        return False

    def clean_cell_output(cell):
        """Clean cell output."""
        cell.outputs = []
        cell.execution_count = None
        # Remove metadata associated with output
        if "metadata" in cell:
            for field in {"collapsed", "scrolled"}:
                cell.metadata.pop(field, None)
        return cell

    if p.is_file() and p.suffix == ".ipynb":
        # Read notebook
        cleared = False
        with p.open("r") as f:
            nb = nbformat.read(f, nbformat.NO_CONVERT)
            if blitz:
                nb.cells = [clean_cell_output(cell) for cell in nb.cells]
                # Always clean and rewrite these notebooks
                cleared = True
            else:
                nb.cells = [
                    (
                        clean_cell_output(cell)
                        if (istagged(cell, tags) and not retain)
                        or (not istagged(cell, tags) and retain)
                        else cell
                    )
                    for cell in nb.cells
                ]
                cleared = any(
                    ((istagged(cell, tags) and not retain) or (not istagged(cell, tags) and retain)) for cell in nb.cells
                )

        if cleared:
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
    default=False,
    help="Clear all code cell outputs irrespective of other settings.",
)
@click.option(
    "--retain/--no-retain",
    default=False,
    help="Retain or delete output by tag. By default, we delete (--no-retain)",
)
@click.option(
    "--tag",
    "-t",
    multiple=True,
    help="Specify tags. You can use this option multiple times.",
)
def code_output_cleaner(paths, recursive, blitz, retain, tag):
    """Clean code cells."""
    tags = list(tag)
    for path in paths:
        # Parse notebooks
        nb_dir = Path(path)
        if nb_dir.is_file():
            _process(nb_dir, blitz, retain, tags)
        elif recursive:
            exclude = set([])
            for dirname, subdirs, files in os.walk(path, topdown=True):
                subdirs[:] = [d for d in subdirs if d not in exclude]
                exclude_hidden_items(subdirs)
                for p in files:
                    _process(Path(dirname) / p, blitz, retain, tags)
        else:
            for p in nb_dir.iterdir():
                _process(p, blitz, retain, tags)
