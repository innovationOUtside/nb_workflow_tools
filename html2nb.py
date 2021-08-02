#Inspired by https://stackoverflow.com/a/47138762/454773

from bs4 import BeautifulSoup
import json
import click
from pathlib import Path
import nbformat

@click.command()
@click.argument('path', type=click.Path(exists=True))
def html2ipynb(path):
    """Convert notebook HTML format to ipynb."""
    # I don't understand why click isn't handling this?
    path = Path(path)
    if path.is_file() and path.suffix == '.html':
        print(f"Checking {path}")
        # Read notebook
        with path.open('r') as f:
            nb = nbformat.v4.new_notebook()

            html = f.read()
            soup = BeautifulSoup(html, 'lxml')
            
            for d in soup.findAll("div"):
                if 'class' in d.attrs.keys():
                    for clas in d.attrs["class"]:
                        if clas in ["text_cell_render", "input_area"]:
                            # code cell
                            if clas == "input_area":
                                cell = nbformat.v4.new_code_cell(d.get_text())
                                nb.cells.append(cell)

                            else:
                                cell = nbformat.v4.new_code_cell(d.decode_contents())
                                nb.cells.append(cell)

    
    outpath = path.with_suffix('.ipynb')
    nbformat.write(nb, outpath.open('w'))