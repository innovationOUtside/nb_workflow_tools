# Simple Routine to check that cells are tagged
import os
from tm351_nb_utils import exclude_hidden_items

import click
import os

import nbformat
from pathlib import Path


def _process(p, tags):
    """Check code cell tags."""

    def istagged(cell, tags):
        """Identify if cell is tagged for cleaning."""
        if (
            cell.cell_type == "code"
            and "metadata" in cell
            and "tags" in cell["metadata"]
        ):
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
            i=0
            for cell in nb.cells:
                if cell.cell_type != "code":
                    continue
                i=i+1
                tagged = False
                _tags = []
                if "metadata" in cell and "tags" in cell["metadata"]:
                    tagged = bool(set(cell["metadata"]["tags"]) & set(tags))
                    _tags = cell["metadata"]["tags"]
                if not tagged:
                    print(f"Notebook {p} code cell {i} is not tagged with any of {tags}. Tagged with: {_tags}")


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(resolve_path=False))
@click.option(
    "--recursive/--no-recursive", default=True, help="Recursive search of directories."
)
@click.option(
    "--tag",
    "-t",
    multiple=True,
    help="Specify tags. You can use this option multiple times.",
)
def check_code_cell_tags(paths, recursive, tag):
    """Check code cell tags. Report if cells not tagged or incorrectly tagged."""
    tags = list(tag)
    for path in paths:
        # Parse notebooks
        nb_dir = Path(path)
        if nb_dir.is_file():
            _process(nb_dir, tags)
        elif recursive:
            exclude = set([])
            for dirname, subdirs, files in os.walk(path, topdown=True):
                subdirs[:] = [d for d in subdirs if d not in exclude]
                exclude_hidden_items(subdirs)
                for p in files:
                    _process(Path(dirname) / p, tags)
        else:
            for p in nb_dir.iterdir():
                _process(p, tags)
