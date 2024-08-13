import os
from tm351_nb_utils import exclude_hidden_items

import click
import os

import nbformat
from pathlib import Path
import re

# From Cluadue.ai
def _process(p, max_heading_level=3):
    """
    Process a Jupyter notebook file, splitting markdown cells at headings.

    :param p: Path to the notebook file
    :param max_heading_level: Maximum heading level to split at (default: 3)
    """
    if p.is_file() and p.suffix == ".ipynb":
        with p.open("r") as f:
            nb = nbformat.read(f, nbformat.NO_CONVERT)

        new_cells = []
        updated = False
        for cell in nb.cells:
            if cell["cell_type"] == "markdown":
                source = (
                    cell["source"]
                    if isinstance(cell["source"], str)
                    else "".join(cell["source"])
                )

                # Split the source at headings
                pattern = r"^(#{1," + str(max_heading_level) + r"}\s+.+)$"
                parts = re.split(pattern, source, flags=re.MULTILINE)
                # If there are no splits, keep the cell as is
                if len(parts) == 1:
                    new_cells.append(cell)
                else:
                    updated = True
                    # The first part might not start with a heading
                    if parts[0]:
                        new_cells.append(nbformat.v4.new_markdown_cell(parts[0]))

                    # Process the rest of the parts
                    for i in range(1, len(parts), 2):
                        heading = parts[i] + " " + parts[i + 1].lstrip()
                        new_cells.append(nbformat.v4.new_markdown_cell(heading))
            else:
                new_cells.append(cell)

        if updated:
            nb.cells = new_cells
            print(f"Updating {p}")
            with p.open("w") as f:
                nbformat.write(nb, f)
        else:
            print(f"No changes needed for {p}")


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(resolve_path=False))
@click.option(
    "--maxheading",
    type=int,
    default=3,
    help="Maximum heading level to split at (1 to 6); default=3.",
)
@click.option(
    "--recursive/--no-recursive", default=True, help="Recursive search of directories."
)
def section_splitter(paths, maxheading, recursive):
    """Split cells at section headings."""
    for path in paths:
        # Parse notebooks
        nb_dir = Path(path)
        if nb_dir.is_file():
            _process(nb_dir, maxheading)

        if recursive:
            exclude = set([])
            for dirname, subdirs, files in os.walk(path, topdown=True):
                subdirs[:] = [d for d in subdirs if d not in exclude]
                exclude_hidden_items(subdirs)
                for p in files:
                    _process(Path(dirname) / p, maxheading)
        else:
            for p in nb_dir.iterdir():
                _process(p, maxheading)
