## Simple Routine to handle line separator (--) at start of cell
# Either by replacing it with a valid spearator, or remove it)

import os
from tm351_nb_utils import exclude_hidden_items

import click
import os

import nbformat
from pathlib import Path
import re
from .utils import defensive_open

def _process(p, retain):
    """Handle cells and clean separators as required."""
    try:
        if p.is_file() and p.suffix == ".ipynb":
            updated = False
 
            # Read notebook
            with defensive_open(p) as f:
                nb = nbformat.read(f, nbformat.NO_CONVERT)
                for cell in nb["cells"]:

                    if cell["cell_type"] == "markdown":
                        source = cell["source"]
                        if isinstance(source, list):
                            source = "".join(source)
                        pattern = r"^-+\s*\s*(?:\n|$)"
                        needs_repair = re.match(pattern, source)
                        if bool(needs_repair):
                            if retain:
                                new_source = f"\n{source}"
                            else:
                                pattern = r"^-+\s*\n?"
                                match = re.search(pattern, source)
                                new_source = source[match.end() :]

                            # Update the cell source
                            if isinstance(cell["source"], list):
                                cell["source"] = [new_source]
                            else:
                                cell["source"] = new_source

                            updated = True
            if updated:
                print(f"Updating {p}")
                nbformat.write(nb, p.open("w"), nbformat.NO_CONVERT)
    except Exception as e:
        print(f"Error trying to clean separator in {p}: {str(e)}")

@click.command()
@click.argument("paths", nargs=-1, type=click.Path(resolve_path=False))
@click.option(
    "--retain/--no-retain",
    default=True,
    help="Retain (fix) separator or delete it.",
)
@click.option(
    "--recursive/--no-recursive", default=True, help="Recursive search of directories."
)
def separator_cleaner(paths, retain, recursive):
    """Clean separators at start of cell."""
    for path in paths:
        # Parse notebooks
        nb_dir = Path(path)
        if nb_dir.is_file():
            _process(nb_dir, retain)

        if recursive:
            exclude = set([])
            for dirname, subdirs, files in os.walk(path, topdown=True):
                subdirs[:] = [d for d in subdirs if d not in exclude]
                exclude_hidden_items(subdirs)
                for p in files:
                    _process(Path(dirname) / p, retain)
        else:
            for p in nb_dir.iterdir():
                _process(p, retain)
