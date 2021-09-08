import click
from pathlib import Path
import nbformat
from nbformat.v4.convert import random_cell_id

#This is a precautionary step...
# Try not to clobber files we may have created previously
import os
import warnings

def listify(item):
    ''' If presented with a string and a list is required, make a list... '''
    item = [] if item is None else item
    #We may be passed a tuple - in which case, listify...
    item = list(item) if isinstance(item,(list,tuple)) else [item]
    return item


# Merge notebooks
@click.command()
@click.option("--outfile","-o", default="merged_notebook.ipynb", type=click.Path(resolve_path=False))
@click.argument('files', nargs=-1)
def nb_merger(outfile, files):
    """Merge two or more notebooks. Note that this may overwrite a pre-existing file."""
    # Opinionated on this
    version = 4 #nbformat.NO_CONVERT
    files = listify(files)

    if len(files) < 2:
        print(f"You need to pass at least two notebook filenames in order to merge them...")
        return

    # Reading the notebooks
    notebooks = [nbformat.read(nb, version) for nb in files]

    # Create new (merged) notebook
    nb_merged = nbformat.v4.new_notebook(metadata=notebooks[0].metadata)

    # Concatenate notebooks
    nb_merged.cells = []
    for notebook in notebooks:
        nb_merged.cells.extend(notebook.cells)

    for i, _ in enumerate(nb_merged.cells):
        nb_merged.cells[i]["id"] = random_cell_id()
 
    # Validate - exception if we fail
    nbformat.validate(nb_merged)

    # Save new notebook 
    nbformat.write(nb_merged, outfile)

# Split notebooks
@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--splitter", default="#--SPLITHERE--", help="String to split on (default: #--SPLITHERE--")
@click.option('--overwrite/--no-overwrite',default=False, help='Overwrite pre-existing files')
def nb_splitter(path, splitter, overwrite):
    """Split a notebook at a splitpoint marker.
    Note that this may overwrite pe-existing files.
    """

    f = Path(path)
    if f.is_file() and f.suffix == '.ipynb' :
            print(f"Checking {f}")
    else:
        print("I was expecting a Jupyter notebook .ipynb file...")
        return

    # Opinionated on this
    version = 4 #nbformat.NO_CONVERT
    nb = nbformat.read(path, as_version=version)

    #Make a copy of the notebook, just in case...
    nb2 = nb.copy()

    #We are going to see if we can split the notebook into separate parts
    parts=[]

    #Each part will contain the cells for the part
    #The rest of the notebook structure, (notebook metadata etc) will be copied from the original notebook
    partcells = []

    #Iterate through all the cells
    for cell in nb2['cells']:
        #Check for a splitline marker - go defensive!
        splitline = cell['source'].upper().strip().replace(" ","") == splitter
        #If we're not at a split line,
        if not splitline:
            #Append the cell to the cell list for this part
            partcells.append(cell)
        else:
            #Otherwise, save the cells to the part...
            parts.append(partcells)
            #...and create a new part cells list
            partcells=[]

    #Commit the final set of cells to the final part
    parts.append(partcells)

    #We can provide more warning notices...
    caution = False

    for ix, cells in enumerate(parts):
        part_fn = path.replace('.ipynb','_PART {}.ipynb'.format(ix+1))
        if os.path.isfile(part_fn) and not overwrite:
            raise Exception('File {} already exists. Set: overwrite=True. Exiting...'.format(part_fn))
        elif caution:
            warnings.warn("You were warned... The following file will be overwritten: {}".format(part_fn))
            
        #For each part, write out a separate notebook containing just the cells in that part. 
        nb_out = nb.copy()
        nb_out['cells'] = cells
        # Validate - exception if we fail
        nbformat.validate(nb_out)
        print('Writing {}...'.format(part_fn))
        nbformat.write(nb_out, part_fn, version)

