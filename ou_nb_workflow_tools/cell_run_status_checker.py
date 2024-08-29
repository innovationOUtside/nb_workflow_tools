# # Check cell run status issues
import os
from tm351_nb_utils import exclude_hidden_items

import click
import os
import re
import nbformat
from pathlib import Path


def _process(p, check_run, check_not_run):
    """Process cell run status indications.

        - code cell not run (no cell run index)
        - cells run out of order (based on cell run index)
        - cell run index != code cell number in notebook

    """

    # Via chatgpt
    def _has_non_comment_text(s):
        # Regular expression to remove single-line comments
        s_no_single_line_comments = re.sub(r"#.*", "", s)

        # Regular expression to remove multi-line comments (triple single quotes or double quotes)
        s_no_comments = re.sub(
            r'""".*?"""|\'\'\'.*?\'\'\'', "", s_no_single_line_comments, flags=re.DOTALL
        )

        # Check if there is any text left that is not just whitespace
        return bool(re.search(r"\S", s_no_comments)), s_no_comments.strip()

    def _get_reports(p, nb, check_run, check_not_run):
        reports = []
        _i = 0  # Code cell count
        _run_ix_list = []
        for i, cell in enumerate(nb["cells"]):
            if cell["cell_type"] == "code":
                _i = _i + 1
            else:
                continue
            _x = -999
            if "execution_count" in cell:
                _x = cell["execution_count"]
                _run_ix_list.append((_i, _x))
            if check_run:
                if _x is None:
                    _report = f"Code cell {_i}: not executed"
                    reports.append(_report)
                elif _x != _i:
                    _report = f"Code cell {_i}: execute count mismatch {_x}!={_i}"
                    reports.append(_report)
            if check_not_run:
                if _x is not None:
                    _report = f"Code cell {_i} has been executed: {_i}/{_x}"
                    reports.append(_report)
                if "outputs" in cell and cell["outputs"]:
                    _report = f"Code cell {_i} has been executed — cell outputs on {_i}/{_x}"
                    reports.append(_report)
         
            source = cell.get("source", "")
            # Cope with v4 and v5 notebooks
            if isinstance(source, list):
                source = "".join(source).strip()
            if not source:
                _report = f"Code cell {_i}({i})/{_x} is empty"
                reports.append(_report)
            else:
                actual_code = _has_non_comment_text(source)
                if not actual_code[0]:
                    _report = f"Code cell {_i}({i})/{_x} only contains comments"
                    reports.append(_report)
            if "outputs" in cell:
                for output in cell["outputs"]:
                    if "name" in output and output["name"] == "stderr":
                        msg = output["text"].split("\n")[0]
                        _report = f"Warning in cell {_i}/{_x}: {msg}"
                        reports.append(_report)
                    elif "output_type" in output and output["output_type"] == "error":
                        msg = output["ename"] if "ename" in output else "???"
                        _report = f"Warning in cell {_i}({i})/{_x}: {msg}"
                        reports.append(_report)

        # Get actually executed cells
        executed_cells = [c for c in _run_ix_list if c[1] is not None]
        # Check ascending order
        out_of_order_pairs = []
        for i in range(len(executed_cells) - 1):
            if executed_cells[i][1] >= executed_cells[i + 1][1]:
                out_of_order_pairs.append((executed_cells[i], executed_cells[i + 1]))

        if out_of_order_pairs:
            for oop in out_of_order_pairs:
                reports.append(f"Out of order cells: code cell {oop[1]} follows {oop[0]} ")
        return reports

    fixes = []

    if p.is_file() and p.suffix == ".ipynb":
        # Read notebook
        with p.open("r") as f:
            nb = nbformat.read(f, nbformat.NO_CONVERT)
            _fixes = _get_reports(p, nb, check_run, check_not_run)
            #if not _fixes:
            #    _fixes = ["No cell run status issues"]
            if _fixes:
                fixes.append(f"\nCell run status checks for {p}:\n\t"+"\n\t".join(_fixes)+"\n")

        if fixes:
            print("\n".join(fixes)) 


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(resolve_path=False))
@click.option(
    "--recursive/--no-recursive", default=True, help="Recursive search of directories."
)
@click.option("--check-run", "-r", is_flag=True, help="Check if cells run.")
@click.option("--check-not-run", "-N", is_flag=True, help="Check if cells are not run.")
def cell_run_status_checker(paths, recursive, check_run, check_not_run):
    """Check cell run status indications."""

    for path in paths:
        # Parse notebooks
        nb_dir = Path(path)
        if nb_dir.is_file():
            _process(nb_dir, check_run, check_not_run)
        elif recursive:
            exclude = set([])
            for dirname, subdirs, files in os.walk(path, topdown=True):
                subdirs[:] = [d for d in subdirs if d not in exclude]
                exclude_hidden_items(subdirs)
                for p in files:
                    _process(Path(dirname) / p, check_run, check_not_run)
        else:
            for p in nb_dir.iterdir():
                _process(p, check_run, check_not_run)
