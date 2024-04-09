# # Simple Routine to clear a key from metadata
import os
from tm351_nb_utils import exclude_hidden_items

import click
import os

import nbformat
from pathlib import Path

def _process(p, tag):
    """Handle cell figure output autotagging."""

    if p.is_file() and p.suffix == '.ipynb':
        updated = False

        # Read notebook
        with p.open('r') as f:

            nb = nbformat.read(f, nbformat.NO_CONVERT)
            for _, cell in enumerate(nb['cells']):
                if cell["cell_type"]=="code" and cell.get("outputs"):
                    figure_output = False
                    for output in cell["outputs"]:
                        if output["output_type"] == "display_data" and "image/png" in output["data"]:
                            figure_output = True
                    if figure_output:
                        if "tags" not in cell["metadata"]:
                            cell["metadata"]["tags"] = [tag]
                            updated = True
                        elif tag not in cell["metadata"]["tags"]:
                            cell["metadata"]["tags"].append(tag)
                            updated = True

        if updated:
            print(f"Updating {p}")
            nbformat.write(nb, p.open('w'), nbformat.NO_CONVERT)



@click.command()
@click.argument('path', type=click.Path(resolve_path=False))
@click.option('--tag', '-t', type=str, default="nbval-figure", help='Tag to label figure output cells.')
@click.option('--recursive/--no-recursive', default=True, help='Recursive search of directories.')
def figure_autotagger(path, tag, recursive):
    """Autotag figure output cell."""

    # Parse notebooks
    nb_dir = Path(path)

    if recursive:
        exclude = set([])
        for dirname, subdirs, files in os.walk(path, topdown=True):
            subdirs[:] = [d for d in subdirs if d not in exclude]
            exclude_hidden_items(subdirs)
            for p in files:
                _process(Path(dirname) / p, tag)
    else:
        for p in nb_dir.iterdir():
            _process(p, tag)

