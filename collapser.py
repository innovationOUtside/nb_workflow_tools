# # Simple Routine to try to ensure headings are collapsed
#
# The collapsible headings extension will automatically collapse items below a heading,
# up to a heading of the same or higher level, if a cell has a
# `heading_collapsed=true` metadata element.
#
# Operationally, the extension then adds a `hidden=true` cell metadata element.
# # Whilst we don't need to add this, it is perhaps useful if the collapsible heading extension / template
# is not available, e.g. for Jupyter Book.

import os
from tm351_nb_utils import exclude_hidden_items

import click
import os

import nbformat
from pathlib import Path

def _process(p, cnb):
    """Handle cell collapse."""
    collapse_metadata = "heading_collapsed" if cnb else "jp-MarkdownHeadingCollapsed"
    tag_set = {"style-activity", "style_activity"}
    metadata_set = {"activity"}

    possibles = ["# Our solution",  "# Answer", "click on the triangle symbol"]
    possibles = [p.lower() for p in possibles]

    if p.is_file() and p.suffix == '.ipynb':
        updated = False

        # Read notebook
        with p.open('r') as f:
            # print(f"Trying {p}")

            nb = nbformat.read(f, nbformat.NO_CONVERT)

            answer_block = False
            answer_header = False
            # header_level = 0
            # Enumerate through cells
            for i, cell in enumerate(nb['cells']):
                if ('tags' in cell["metadata"] and tag_set.intersection(set(cell["metadata"]["tags"])))                                 or metadata_set.intersection(set(cell["metadata"])):
                    # For each markdown cell
                    if cell['cell_type']=='markdown':
                        # Hacky attempt at identifying an answer header
                        if cell['source'].startswith("#"):
                            if any(ans in cell['source'].lower() for ans in possibles):
                                # header_level = len(cell['source'].split(" ")[0])
                                answer_header = True
                elif 'tags' in cell["metadata"] and "precollapse" in cell["metadata"]["tags"]                             and cell['source'].startswith("#"):
                    # This is a convenience thing posting a new "precollapse" tag
                    answer_header = True
                else:
                    answer_block = False
                    answer_header = False
                    # header_level = 0

                # For all cells - collapse if answer
                if answer_header:
                    updated = True
                    answer_header = False
                    answer_block = True
                    cell["metadata"][collapse_metadata] = True
                # Whilst there is a metadata flag to show a cell is hidden
                # this is automatically set by the collapsible headings extension
                # So the following is redundant, though may be useful if the collapsible
                # heading extentsion / template is not available, e.g. for Jupyter Book
                elif answer_block and cnb:
                    cell["metadata"]["hidden"] = True

        if updated:
            print(f"Updating {p}")
            nbformat.write(nb, p.open('w'), nbformat.NO_CONVERT)


@click.command()
@click.argument("path", type=click.Path(resolve_path=False))
@click.option(
    "--recursive/--no-recursive", default=True, help="Recursive search of directories."
)
@click.option(
    "--cnb/--no-cnb", default=False, help="Use classic notebook extension metadata value (default: use no-cnb (JupyterLab/nb7) format)."
)
def activity_collapser(path, recursive, cnb):
    """Collapse activity answers."""

    # Parse notebooks
    nb_dir = Path(path)

    if recursive:
        exclude = set([])
        for dirname, subdirs, files in os.walk(path, topdown=True):
            subdirs[:] = [d for d in subdirs if d not in exclude]
            exclude_hidden_items(subdirs)
            for p in files:
                _process(Path(dirname) / p, cnb)
    else:
        for p in nb_dir.iterdir():
            _process(p, cnb)
