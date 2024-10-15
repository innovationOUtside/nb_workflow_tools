import os
from tm351_nb_utils import exclude_hidden_items

import click
import os
import re
import nbformat
from urllib.parse import quote
from pathlib import Path


def replace_img_tags(markdown_text):
    def img_to_myst(match):
        attributes = match.groupdict()
        src = attributes.get("src", "")
        alt = attributes.get("alt", "")
        height = attributes.get("height", "")
        width = attributes.get("width", "")

        # URL encode the src path
        encoded_src = quote(src)

        myst = f"```{{image}} {encoded_src}\n"
        if alt:
            myst += f":alt: {alt}\n"
        if height:
            myst += f":height: {height}\n"
        if width:
            myst += f":width: {width}\n"
        myst += "```"
        return myst

    markdown_text_ = markdown_text
    # Regex to match img tags with attributes in any order
    img_pattern = r'<img\s+(?P<attrs>(?:src=["\'][^"\']+["\']|alt=["\'][^"\']*["\']|height=["\'][^"\']+["\']|width=["\'][^"\']+["\']|\s+)+)[^>]*>'

    # First, find all img tags
    img_tags = re.finditer(img_pattern, markdown_text)

    # Process each img tag
    for img_tag in img_tags:
        attrs = img_tag.group("attrs")

        # Extract individual attributes
        src_match = re.search(r'src=["\']([^"\']+)["\']', attrs)
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', attrs)
        height_match = re.search(r'height=["\']([^"\']+)["\']', attrs)
        width_match = re.search(r'width=["\']([^"\']+)["\']', attrs)

        # Create a dictionary with the extracted attributes
        attributes = {
            "src": src_match.group(1) if src_match else "",
            "alt": alt_match.group(1) if alt_match else "",
            "height": height_match.group(1) if height_match else "",
            "width": width_match.group(1) if width_match else "",
        }

        # Replace the img tag with MyST syntax
        markdown_text = markdown_text.replace(
            img_tag.group(0),
            img_to_myst(type("Match", (), {"groupdict": lambda: attributes})),
        )

    return markdown_text, markdown_text_ == markdown_text


def replace_anchor_tags(markdown_text):
    def anchor_to_markdown(match):
        href = match.group("href")
        text = match.group("text")
        return f"[{text}]({href})"

    markdown_text_ = markdown_text
    # Regex to match anchor tags
    anchor_pattern = r'<a\s+href=["\'](?P<href>[^"\']+)["\'][^>]*>(?P<text>.*?)</a>'
    markdown_text = re.sub(anchor_pattern, anchor_to_markdown, markdown_text)
    return markdown_text, markdown_text_ == markdown_text


def replace_tags(markdown_text):
    # Replace img tags
    markdown_text, changed_img = replace_img_tags(markdown_text)

    # Replace anchor tags
    markdown_text, changed_anchor = replace_anchor_tags(markdown_text)

    return markdown_text, any([changed_img, changed_anchor])


def _process(p):
    """Replace HTML tags with MyST equivalent:

    - <img /> with {image} block;
    - <a> anchor with []() md link

    """

    if p.is_file() and p.suffix == ".ipynb":
        # Read notebook
        with p.open("r") as f:
            nb = nbformat.read(f, nbformat.NO_CONVERT)

        changed = False

        # Process each cell
        for cell in nb.cells:
            if cell.cell_type == "markdown":
                cell.source, changed_ = replace_tags(cell.source)
            changed = changed_ or changed
        if changed:
            # Write the modified notebook
            with p.open("w") as f:
                nbformat.write(nb, f)
            print(f"Updated {p}")

    else:
        pass
        #print(f"{p} is not a Jupyter notebook file.")


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(resolve_path=False))
@click.option(
    "--recursive/--no-recursive", default=True, help="Recursive search of directories."
)
def html_tag_replacer(paths, recursive):
    """Replace HTML image and anchor tags with MyST equivalent."""

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
