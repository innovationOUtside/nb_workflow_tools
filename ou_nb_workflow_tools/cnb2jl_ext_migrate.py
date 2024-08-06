import click
import nbformat
from pathlib import Path

@click.command()
@click.argument("paths", nargs=-1, type=click.Path(resolve_path=False))
@click.option(
    "--recursive/--no-recursive", default=True, help="Recursive search of directories."
)
@click.option(
    "--hidden/--no-hidden", default=False, help="Include hidden files and directories."
)
def fix_collapse_headings_metadata(paths, recursive, hidden):
    """Fix collapsible headings metadata."""

    def _process(p):
        """Fix metadata in notebook cells."""

        if p.is_file() and p.suffix == ".ipynb":
            updated = False

            # Read notebook
            with p.open("r") as f:
                # print(f"Trying {p}")
                # heading_collapsed: true -> jp-MarkdownHeadingCollapsed: true
                nb = nbformat.read(f, nbformat.NO_CONVERT)
                for _, cell in enumerate(nb["cells"]):
                    if "heading_collapsed" in cell["metadata"]:
                        cell["metadata"]["jp-MarkdownHeadingCollapsed"] = cell[
                            "metadata"
                        ]["heading_collapsed"]
                        cell["metadata"].pop("heading_collapsed", None)
                        updated = True

            if updated:
                print(f"Fixing collapsible headings metadata in {p}")
                nbformat.write(nb, p.open("w"), nbformat.NO_CONVERT)

    for path in paths:
        # Parse notebooks
        nb_dir = Path(path)
        if nb_dir.is_file():
            _process(nb_dir)
        if recursive:
            for p in nb_dir.rglob("*"):
                if hidden:
                    _process(p)
                else:
                    if not any(part.startswith(".") for part in p.parts):
                        _process(p)

        else:
            for p in nb_dir.iterdir():
                _process(p)
