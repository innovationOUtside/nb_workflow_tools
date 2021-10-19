# # Simple Routine to try to ensure tag toolbar is collapsed
import os
from tm351_nb_utils import exclude_hidden_items

import click
import os

import nbformat
from pathlib import Path

def _process(p):
    """Handle tag toolbar collapse."""

    if p.is_file() and p.suffix == '.ipynb':
        updated = False

        # Read notebook
        with p.open('r') as f:
            #print(f"Trying {p}")
            
            nb = nbformat.read(f, nbformat.NO_CONVERT)
            if "celltoolbar" in nb.metadata and nb.metadata.celltoolbar=="Tags":
                nb.metadata.pop("celltoolbar", None)
                updated = True

        if updated:
            print(f"Updating {p}")
            nbformat.write(nb, p.open('w'), nbformat.NO_CONVERT)



@click.command()
@click.argument('path', type=click.Path(resolve_path=False))
@click.option('--recursive/--no-recursive',default=True, help='Recursive search of directories.')
def tag_toolbar_collapser(path, recursive):
    """Collapse tags toolbar."""

    # Parse notebooks
    nb_dir = Path(path)
    
    if recursive:
        exclude = set([])
        for dirname, subdirs, files in os.walk(path, topdown=True):
            subdirs[:] = [d for d in subdirs if d not in exclude]
            exclude_hidden_items(subdirs)
            for p in files:
                _process(Path(dirname) / p)
    else:
        for p in nb_dir.iterdir():
            _process(p)

