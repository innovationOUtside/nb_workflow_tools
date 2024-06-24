## Simple Routine to strip handle line separator (--) at strat of cell
# Either by replacing it with a valid spearator, or remove it)

import os
from tm351_nb_utils import exclude_hidden_items

import click
import os

import nbformat
from pathlib import Path
import re

def _process(p, retain):
    """Handle cells and clean separators as required."""

    if p.is_file() and p.suffix == ".ipynb":
        updated = False

        # Read notebook
        with p.open("r") as f:

            nb = nbformat.read(f, nbformat.NO_CONVERT)
            for _, cell in enumerate(nb["cells"]):
                if cell["cell_type"] == "markdown":
                    pattern = r"^-+\s*(?:\n.*)?$"
                    needs_repair = re.match(pattern, cell["source"])
                    if bool(needs_repair):
                        if retain:
                            cell["source"] = f'\n{cell["source"]}'
                        else:
                            pattern = r"^-+\s*\n?"
                            match = re.search(pattern, cell["source"])
                            cell["source"] = cell["source"][match.end():]
                        updated = True   
        if updated:
            print(f"Updating {p}")
            nbformat.write(nb, p.open("w"), nbformat.NO_CONVERT)


@click.command()
@click.argument("path", type=click.Path(resolve_path=False))
@click.option(
    "--retain/--no-retain",
    default=True,
    help="Retain (fix) separator or delete it.",
)
@click.option(
    "--recursive/--no-recursive", default=True, help="Recursive search of directories."
)
def separator_cleaner(path, retain, recursive):
    """Clean separators at start of cell."""

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
