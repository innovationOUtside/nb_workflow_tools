# # Simple Routine to clear a ky from metadata
import os
from tm351_nb_utils import exclude_hidden_items

import click
import os

import nbformat
from pathlib import Path

def _process(p, keys):
    """Handle metadata key cleaner."""

    if p.is_file() and p.suffix == '.ipynb':
        updated = False

        # Read notebook
        with p.open('r') as f:
            #print(f"Trying {p} with {keys}")

            nb = nbformat.read(f, nbformat.NO_CONVERT)
            for _, cell in enumerate(nb['cells']):
                for key in keys:
                    if key in cell["metadata"]:
                        cell["metadata"].pop(key, None)
                        updated = True

        if updated:
            print(f"Updating {p}")
            nbformat.write(nb, p.open('w'), nbformat.NO_CONVERT)


@click.command()
@click.argument("path", type=click.Path(resolve_path=False))
@click.argument("keys", type=str, nargs=-1)
@click.option(
    "--recursive/--no-recursive", default=True, help="Recursive search of directories."
)
def cell_metadata_key_cleaner(path, keys, recursive):
    """Clean one or more metadata items by key from cell ."""
    keys = list(keys)
    # Parse notebooks
    nb_dir = Path(path)
    if nb_dir.is_file():
        _process(nb_dir, keys)
    elif recursive:
        exclude = set([])
        for dirname, subdirs, files in os.walk(path, topdown=True):
            subdirs[:] = [d for d in subdirs if d not in exclude]
            exclude_hidden_items(subdirs)
            for p in files:
                _process(Path(dirname) / p, keys)
    else:
        for p in nb_dir.iterdir():
            _process(p, keys)
