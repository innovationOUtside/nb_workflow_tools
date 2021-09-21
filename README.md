# ou-tm351 - `nb_workflow_tools`

First attempt at some command line utils to support Jupyter notebook workflows for OU course TM351.

To install:

`pip3 install git+https://github.com/innovationOUtside/nb_workflow_tools`

To upgrade a current installation to the latest repo version without updating dependencies:

`pip3 install --upgrade --no-deps git+https://github.com/innovationOUtside/nb_workflow_tools`


For other utility toolbelts, see for example:

- [`choldgraf/nbclean`](https://github.com/choldgraf/nbclean)

## Tools

A variety of tools are bundled as CLI commands published via the package or informally sketched in various Jupyter notebooks in the `notebooks` directory.

### Zipper

Tools for previewing the files contained in a zip file and creating new zip files.

```
Usage: tm351zipview [OPTIONS] [FILENAME]...

  List the contents of one or more specified zipfiles.

Options:
  --help  Show this message and exit.
```

The `tm351zipview` reports four columns: file_size, file compressed size, datetime and filename.

```
Usage: tm351zip [OPTIONS] PATH ZIPFILE

  Create a zip file from the contents of a specified directory.

  The zipper can optionally run a notebook processor on notebooks before
  zipping them to check that all cells are run or all cells are cleared.

Options:
  -r, --file-processor [clearOutput|runWithErrors]
  -H, --include-hiddenfiles       Include hidden files
  -X, --exclude-dir PATH          Exclude specified directory
  -x, --exclude-file PATH         Exclude specified file
  --help                          Show this message and exit.
```


Note - there is a gotcha trying to connect to Github - using Python on Mac: https://stackoverflow.com/a/42098127/454773

```
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

```
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

```
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

### Empinken updater:

Update tag styles used for empinken cells:

```
# Recurse on directory path rewriting .ipynb files with new tag style
upgrade_empinken_tags ./
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

Ensure that notebooks in a directory path have activity answers collapsed using the *Collapsible Headings* classic Jupyter notebook extension. This currently relies on heuristics to detect the answer header cell. Specifically, it should be highlighted as a blue activity cell using the `nb_extension_empinken` activity tool (which adds the `style-activity` tag to a cell) and contains at least some of the following text:

`possibles = ["# Our solution",  "# Answer", "click on the triangle symbol"]`

Usage takes the form: `nb_collapse_activities PATH` and is recursive by default.

```text
Usage: nb_collapse_activities [OPTIONS] PATH

  Collapse activity answers.

Options:
  --recursive / --no-recursive  Recursive search of directories.
  --help                        Show this message and exit.
```
