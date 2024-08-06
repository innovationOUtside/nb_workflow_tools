# # Simple Routine to try to find cell output errors, warnings etc
import os
from tm351_nb_utils import exclude_hidden_items

import click
import os

import nbformat
from pathlib import Path


def _process(p):
    """Spot warning."""
    def _get_warnings(p, nb):
        _trapped_warnings = []
        _warnings = []
        _i = 0 # Code cell count
        for i, cell in enumerate(nb["cells"]):
            if cell['cell_type']=="code":
                _i = _i+1
            if "outputs" in cell:
                for output in cell["outputs"]:
                    if "name" in output and output["name"] == "stderr":
                        msg = output["text"].split("\n")[0]
                        if "tags" in cell["metadata"] and 'raises-exception' in cell["metadata"]["tags"]:
                                _trapped_warnings.append( ( _i, msg) )
                        else:
                            _warnings.append(
                                (_i,
                                    msg,
                                )
                            )
                    elif "output_type" in output and output["output_type"]=="error":
                        
                        msg = output["ename"] if "ename" in output else "???"

                        # _warnings.append(
                        #        (
                        #            _i,
                        #            msg,
                        #        ))
                        if "tags" in cell["metadata"] and "raises-exception" in cell["metadata"]["tags"]:
                                _trapped_warnings.append((_i, msg))
                                print("appended t")
                        else:
                            _warnings.append(
                                (
                                    _i,
                                    msg,
                                )
                            )
        return _warnings, _trapped_warnings

    warnings = []
    trapped_warnings = []

    if p.is_file() and p.suffix == ".ipynb":
        # Read notebook
        with p.open("r") as f:
            nb = nbformat.read(f, nbformat.NO_CONVERT)
            _warnings, _trapped_warnings = _get_warnings(p, nb)
            warnings.extend(_warnings)
            trapped_warnings.extend(_trapped_warnings)
    if trapped_warnings or warnings:
        print(f"\n{p}\n")
        if trapped_warnings:
            print(f"Trapped warnings/errors:")
            for w in trapped_warnings:
                print(w)
            print("\n")
        if warnings:
            print(f"****Untrapped warnings/errors:****")
            for w in warnings:
                print(w)
            print("\n")


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(resolve_path=False))
@click.option(
    "--recursive/--no-recursive", default=True, help="Recursive search of directories."
)
def stderr_checker(paths, recursive):
    """Spot stderr errors and warnings."""

    for path in paths:
        # Parse notebooks
        nb_dir = Path(path)
        if nb_dir.is_file():
            _process(nb_dir)
        elif recursive:
            exclude = set([])
            for dirname, subdirs, files in os.walk(path, topdown=True):
                subdirs[:] = [d for d in subdirs if d not in exclude]
                exclude_hidden_items(subdirs)
                for p in files:
                    _process(Path(dirname) / p)
        else:
            for p in nb_dir.iterdir():
                _process(p)
