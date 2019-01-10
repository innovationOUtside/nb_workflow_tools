# ou-tm351 - `nb_workflow_tools`

First attempt at some command line utils to support Jupyter notebook workflows for OU course TM351.

To install:

`pip3 install git+https://github.com/innovationOUtside/nb_workflow_tools`

To upgrade a current installation to the latest repo version without updating dependencies:

`pip3 install --upgrade --no-deps git+https://github.com/innovationOUtside/nb_workflow_tools`

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
