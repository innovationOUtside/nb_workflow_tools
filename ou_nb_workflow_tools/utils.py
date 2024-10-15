import os
import jupytext
from pathlib import Path
import io

import codecs


def _dir_file_handler(path, _f, filetype='.md'):
    """Get the filename for a single file on a specified path."""
    f = os.path.join(path, _f)
    if f.endswith(filetype):
        return f
    return None

# TO DO - at the moment assumes markdown
# Need to accommodate notebook
# One approach might be to:
# - accept differnt text inputs (various markdown flavours, ipynb etc)
def detect_nb_doctype(path):
    """Dectect what sort of document we are dealing with."""
    # This is inefficient because we end up opening the file twice?
    with io.open(fp, encoding="utf-8") as f:
        txt = f.read()
        typ = jupytext.formats.divine_format(txt)
    return typ
# - cast to notebook with Jupytext
# - process notebook
# - rewrite output with same flavour as input
def _dir_handler(path):
    """Handle all the notebooks in a specific directory."""
    filelist=[]
    for _f in os.listdir(path):
        fn = _dir_file_handler(path, _f)
        if fn:
            filelist.append(fn)
    return filelist

def _path_full_processor(path):
    """Process file path."""
    for fn in _dir_handler(path):
        # Read file
        with open(fn, 'r') as f:
            # Process File
            txt = f.read()
            txt = process_headers(txt)
            txt = process_typos(txt, word_replacement, case_replacement)

        with open(fn, 'w') as f:
            # Write File
            f.write(txt)


def detect_encoding(file_path):
    encodings = ["utf-8", "ascii", "latin-1", "utf-16", "utf-32"]
    for encoding in encodings:
        print(f"trying to open file as {encoding}")
        try:
            with codecs.open(file_path, "r", encoding=encoding) as file:
                file.read()
            print(f"okay... opened with {encoding}")
            return encoding
        except UnicodeDecodeError:
            print(f"hmm... {encoding} gave UnicodeDecodeError")
            continue
    return None


def defensive_open(p, mode="r"):
    """Open a file with detected encoding or default to 'utf-8'."""
    detected_encoding = detect_encoding(p)
    encoding = "utf-8" if not detected_encoding else detected_encoding
    return p.open(mode, encoding=encoding)
