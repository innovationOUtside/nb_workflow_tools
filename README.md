# ou-tm351 - `nb_workflow_tools`

First attempt at some command line utils to support Jupyter notebook workflows for OU course TM351.

To install: `pip install tm351_nb_utils`

To install the latest version from this repo:

`pip3 install git+https://github.com/innovationOUtside/nb_workflow_tools`

To upgrade a current installation to the latest repo version without updating dependencies:

`pip3 install --upgrade --no-deps git+https://github.com/innovationOUtside/nb_workflow_tools`

For other utility toolbelts, see for example:

- [`choldgraf/nbclean`](https://github.com/choldgraf/nbclean)

## Tools

A variety of tools are bundled as CLI commands published via the package or informally sketched in various Jupyter notebooks in the `notebooks` directory.

### Zipper

Tools for previewing the files contained in a zip file and creating new zip files.

#### Zip file contents preview

```text
Usage: tm351zipview [OPTIONS] [FILENAME]...

  List the contents of one or more specified zipfiles.

Options:
  --warnings / -w   Display warnings
  --help            Show this message and exit.
```

The `tm351zipview` reports four columns: file_size, file compressed size, datetime and filename. If you select `-w` various advisory notices will be displayed about the zip file contents (eg overlong filenames, large files, hidden files).

The warnings report takes the following form:

```text
====== Zip file quality report: /Users/tonyhirst/Documents/GitHub/tm351-undercertainty/notebooks/tm351/test1.zip ======

ERROR: the filepath element "11.A SQL Data Investigation Worked Example (optional).ipynb" in "Part 11 Notebooks/11.A SQL Data Investigation Worked Example (optional).ipynb" is too long (max. 50 chars)
WARNING: "Part 11 Notebooks/.DS_Store" is a hidden file/directory (do you really need it in the zip file?)
ERROR: the filepath element "11.A SQL Data Investigation Worked Example (optional).ipynb" in "Part 11 Notebooks/11.A SQL Data Investigation Worked Example (optional).ipynb" is too long (max. 50 chars)
WARNING: "Part 11 Notebooks/.delme" is a hidden file/directory (do you really need it in the zip file?)
WARNING: "Part 11 Notebooks/.ipynb_checkpoints/" is a hidden file/directory (do you really need it in the zip file?)
WARNING: "Part 11 Notebooks/.ipynb_checkpoints/11.2 subqueries as value and set-checkpoint.ipynb" is a hidden file/directory (do you really need it in the zip file?)
WARNING: "Part 11 Notebooks/sql_movie_data/people.csv": looks quite large file (20.7 MB unzipped, 7.8 MB compressed)
WARNING: "Part 11 Notebooks/sql_movie_data/cast_members.csv": looks quite large file (9.5 MB unzipped, 3.5 MB compressed)
WARNING: "Part 11 Notebooks/sql_movie_data/people-clean-dates.csv": looks quite large file (20.9 MB unzipped, 7.8 MB compressed)
WARNING: "Part 11 Notebooks/sql_movie_data/movies.csv": looks quite large file (5.3 MB unzipped, 2.3 MB compressed)
WARNING: "Part 11 Notebooks/sql_movie_data/crew.csv": looks quite large file (10.2 MB unzipped, 2.3 MB compressed)

===========================

```

#### Zip file creator

```text
Usage: tm351zip [OPTIONS] PATH ZIPFILE

  Create a zip file from the contents of a specified directory.

  The zipper can optionally run a notebook processor on notebooks before
  zipping them to check that all cells are run or all cells are cleared.

Options:
  -r, --file-processor [clearOutput|runWithErrors]
  -H, --include-hiddenfiles       Include hidden files
  -X, --exclude-dir PATH          Exclude specified directory
  -x, --exclude-file PATH         Exclude specified file
  -F, --force                     Force overwriting of pre-existing zip file
  -a, --zip_append                Add to existing zip file
  --help                          Show this message and exit.
```

#### Zip file unzipper

```text
Usage: tm351unzip [OPTIONS] ZIPFILE_PATH [TARGET_DIR]

  Unzip a file into a target directory.

  ZIPFILE_PATH: Path to the zip file to be extracted.
  TARGET_DIR: Directory to extract the contents to (default: zip_output).

Options:
  --help  Show this message and exit.
```

#### Grab files from Github repo

Note - there is a gotcha trying to connect to Github - using Python on Mac: https://stackoverflow.com/a/42098127/454773

```text
Usage: tm351gitrepos [OPTIONS]

  Download files from a specfied branch in a particular git repository.
  
  This command can download files from public Github repositories without authentication, although the API is heavily rate limited if you do no authenticate.

  The download can also be limited to just the contents of a specified directory.
  
  Don't worry that there look to be a lot of arguments - you will be 
  prompted for them if you just run: `tm351gitrepos --auth`

Options:
  --github-user TEXT              Your Github username.
  --password TEXT
  --repo TEXT                     Repository name
  --branch TEXT                   Branch or tag to download
  --directory TEXT                Directory to download (or: all)
  --savedir PATH                  Directory to download repo / repo dir into;
                                  default is dir name
  --file-processor [clearOutput|runWithErrors]
                                  Optionally specify a file processor to be
                                  run against downloaded notebooks.
  --zip / --no-zip                Optionally create a zip file of the
                                  downloaded repository/directory with the
                                  same name as the repository/directory.
  --help                          Show this message and exit.
```

## Testing notebooks

Notebooks are tested using the [`nbval`](https://nbval.readthedocs.io/en/latest/) package. Notebooks should have pre-run cells you want to test against. Running `tm351nbtest` will rerun the notebooks in the environment you run the command in and compares the cell outputs to the previously run cell outputs. (So if you're testing a Docker containerised environment, install this packahge and run the test from the command line *inside the container*.)

Running `tm351nbtest` will print out a list of cells where the cell outputs from a new run of the notebook mismatch the original output. Note that you can “escape” cells that generate known errors by adding a cell tag `raises-exception`. You can also force cells to be ignored by tagging them with the `nbval-ignore-output` tag.

```text
Usage: tm351nbtest [OPTIONS] [TESTITEMS]...

  Test specified notebooks and/or the notebooks in a specified directory 
  or directories (`TESTITEMS`) using the `nbdime` plugin for `py.test`.
  
  Running `tm351nbtest` without
  any specified directory or file will assemble tests recursively from the
  current directory down.

Options:
  -X, --exclude-dir PATH  Do not recurse through specified directory when
                          assembling tests.
  -o, --outfile PATH      Output report file. Leave this blank to display
                          report on command line.
  --help                  Show this message and exit.
```

### Running notebooks and cleaning output cells

```text
Usage: tm351nbrun [OPTIONS] PATH

  Directory processor for notebooks - allows the user to run nbconvert
  operations on notebooks, such as running all cells or clearing all cells.

  To run tests, use: tm351nbtest To zip folders (with the option or running
  notebook processors on zipped files), use: tm351zip

Options:
  -r, --file-processor [clearOutput|runWithErrors]
                                  File processor actions that can be applied 
                                  to notebooks using `nbconvert`
  --outpath PATH                  path to output directory
  --inplace / --no-inplace        Run processors on notebooks inplace
  -X, --exclude-dir PATH          Exclude specified directory
  -x, --exclude-file PATH         Exclude specified file
  --include-hidden / --no-include-hidden
                                  Include hidden files
  --rmdir / --no-rmdir            Check the output directory is empty before
                                  we use it
  --currdir / --no-currdir        Process files in current directory
  --subdirs / --no-subdirs        Process files in subdirectories
  --reportlevel INTEGER           Reporting level
  --auth / --no-auth              By default, run with auth (prompt for
                                  credentials)
  -t, --with-tests                Run tests on notebooks after download
  --help                          Show this message and exit.
```

---

### Empinken updater

Update tag styles used for empinken cells:

```text
# Recurse on directory path rewriting .ipynb files with new tag style
upgrade_empinken_tags ./
```

## Clean cell separator

Some M348 notebooks start a markdown cell with `---` which breaks rendering in JupyterLab with MyST at least. Repair the by either deleting the separator, or prefixing it with blank line.

```text
Usage: nb_cell_separator_fixer [OPTIONS] PATHS

  Clean separators at start of cell.

Options:
  --retain / --no-retain        Retain (fix) separator or delete it.
  --recursive / --no-recursive  Recursive search of directories.
  --help                        Show this message and exit.
```

### Notebook metadata updater - classicnb2jl extension metadata

Patches metadata for extension migration:

- collapsible headings ( `heading_collapsed -> jp-MarkdownHeadingCollapsed`) ; (also run `nb_cell_metadata_strip Part\ 07\ Notebooks hidden` to tidy other metadata sometimes used w/ collapsed cells in OU motebooks)

```text
Usage: cnb_collapse_head_migrate [OPTIONS] PATH

  Fix collapsible headings metadata.

Options:
  --recursive / --no-recursive  Recursive search of directories.
  --hidden / --no-hidden        Include hidden files and
                                directories.
  --help                        Show this message and exit.
```

### Notebook Split and Merge Utilities

Simple tools to merge notebooks and split notebooks on a particular separator.

We can merge two or more notebooks with a command of the form: `nb_merge FILENAME1 FILENAME2 ...`

```text
Usage: nb_merge [OPTIONS] [FILES]...

  Merge two or more notebooks. Note that this may overwrite a pre-existing
  file.

Options:
  -o, --outfile PATH
  --help              Show this message and exit.
```

We can split a notebook at one or mote split points with a command of the form: `nb_split FILENAME`

By default, the split point is `#--SPLITHERE--` or `# --SPLITHERE--`. It should appear as the only item in either a markdown cell or a code cell.

```text
Usage: nb_split [OPTIONS] PATH

  Split a notebook at a splitpoint marker. Note that this may overwrite pe-
  existing files.

Options:
  --splitter TEXT               String to split on (default: #--SPLITHERE--)
  --overwrite / --no-overwrite  Overwrite pre-existing files
  --help                        Show this message and exit.
```

### Ensure Activity Answer Cells Are Collapsed

Ensure that notebooks in a directory path have activity answers collapsed using the *Collapsible Headings* classic Jupyter notebook extension. This currently relies on heuristics to detect the answer header cell, or the presence of a `precollapse` tag in a markdown cell that starts with a heading. Specifically, it should be highlighted as a blue activity cell using the `nb_extension_empinken` activity tool (which adds the `style-activity` tag to a cell) and contains at least some of the following text:

`possibles = ["# Our solution",  "# Answer", "click on the triangle symbol"]`

Usage takes the form: `nb_collapse_activities PATH` and is recursive by default.

```text
Usage: nb_collapse_activities [OPTIONS] PATH

  Collapse activity answers.

Options:
  --recursive / --no-recursive  Recursive search of directories.
  --cnb / --no-cnb              Use classic notebook extension
                                metadata value (default: use no-cnb (JupyterLab/nb7) format).
  -ap, --additional-possibles TEXT
                                Additional possible strings to match. Use quotes; add separate flag per item.
  --help                        Show this message and exit.
```

### Ensure Tags Toolbar is Collapsed

Ensure that notebooks have the tags toolbar view collapsed:

```text
Usage: nb_collapse_tagstoolbar [OPTIONS] PATH

  Collapse tags toolbar.

Options:
  --recursive / --no-recursive  Recursive search of directories.
  --help                        Show this message and exit.
```

### Clean Cell Metadata Tag

Remove metadata object from cell metadata by key, eg `nbdime-conflicts` or `scrolled`

```text
Usage: nb_cell_metadata_strip [OPTIONS] PATH KEY

  Clean metadata from cell.

Options:
  --recursive / --no-recursive  Recursive search of directories.
  --help                        Show this message and exit.
```

## Autotag Figure Cells

Autotag figure output code cells in pre-run notebooks (default tag: `nbval-figure`)

```text
Usage: nb_cell_figure_tagger [OPTIONS] PATH

  Autotag figure output cell.

Options:
  -t, --tag TEXT                Tag to label figure output cells.
  --recursive / --no-recursive  Recursive search of directories.
  --help                        Show this message and exit.
```

## Find Code Cell Warnings, Errors, etc.

Tool for locating notebooks where code cells have an error or warning output. Report displays "tagged" and "untagged" warning cells separately, using the `nbval` cell tag `raises-exception` to identify tagged cells that are expected to raise a warning (TO DO - warn if a `raises-exception` cell *does not* raise a warning).

```text
Usage: nb_cell_stderr_finder [OPTIONS] PATH

  Spot stderr errors and warnings.

Options:
  --recursive / --no-recursive  Recursive search of directories.
  --help                        Show this message and exit.
```

## Empty Cell Cleaner

Clean empty cells. Filters allow:

- clean all cell types (`--blitz`: default `True`)
- specify particular cell types ( any/all of `--md`, `--code`, `--raw`; any of these tags overrides/disables `blitz`)
- clean empty cells at start and end of notebook (default) or `--all` empty cells;
- aggressively treat a cell as empty if it only contains whitespace (default: `True`; retain cells with whitespace by `--no-stripwhitespace`)

For example:

- clean all empty markdown cells: `nb_empty_cell_cleaner --all --md PATH`
- clean all empty code cells at start or end of file: `nb_empty_cell_cleaner --code PATH`

```text
Usage: nb_empty_cell_cleaner [OPTIONS] [PATHS]...

  Clean empty cells.

Options:
  --recursive / --no-recursive    Recursive search of directories.
  --all / --no-all                Remove all empty cells, not just empty
                                  initial and final cells.
  --blitz / --no-blitz            Review all cell types (false if any explicit
                                  cell types are set)
  --code / --no-code              Check code cell.
  --md / --no-md                  Check markdown cell.
  --raw / --no-raw                Check raw cell.
  --stripwhitespace / --no-stripwhitespace
                                  Strip whitespace.
  --help                          Show this message and exit.
```

## Split Cells on Heading

Split cells at a heading. Sp

*Raises the question of if we should merge contiguous markdown cells that are *not* split on a heading?*

```text
Usage: nb_split_sections [OPTIONS] [PATHS]...

  Split cells at section headings.

Options:
  --maxheading INTEGER          Maximum heading level to split at (1 to 6); default=3.
  --recursive / --no-recursive  Recursive search of directories.
  --help                        Show this message and exit.
```
