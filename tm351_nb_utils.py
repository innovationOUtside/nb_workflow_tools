# ou-tm351 - `nb_pub_utils`

# GOTCHA - Python on Mac logging in to Github: https://stackoverflow.com/a/42098127/454773

import click

import os
import shutil
import zipfile
import humanize
import datetime
import github
from tabulate import tabulate
from shlex import quote


import subprocess
def cli_command(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as error:
        return (error.returncode, error.output.decode('utf-8'))
    
    if out!='': return (0, out)

def listify(item):
    ''' If presented with a string and a list is required, make a list... '''
    item = [] if item is None else item
    #We may be passed a tuple - in which case, listify...
    item = list(item) if isinstance(item,(list,tuple)) else [item]
    return item

def exclude_hidden_items(itemlist, exclude_hidden=True):
    ''' Exclude hidden items from ziplist '''
    if exclude_hidden:
        rmlist=[]
        for x in itemlist:
            if x.startswith('.'):
                rmlist.append(x)
        for x in rmlist:
            itemlist.remove(x)

def exclude_items(itemlist, excludes, exclude_hidden=True, ipynb_only=False):
    ''' Exclude items from ziplist '''

    for xd in set(itemlist).intersection(excludes):
        itemlist.remove(xd)

    if ipynb_only:
        for i in [_i for _i in itemlist if not _i.endswith("ipynb")]:
                itemlist.remove(i)
        
    if exclude_hidden: exclude_hidden_items(itemlist)


def notebookTest(path=None, filename=None, dir_excludes=None, file_excludes=None):
    ''' Run notebook tests over explicitly named files and directories.
    '''
    
    #Could probably define this recursively to handle mulitple paths/filenames...
    
    def pathmaker(path,filename):
        if not path or path in ['.']: return filename
        if not isinstance(path,list):
            return '/'.join([path,filename])
    
    sanitiser = """[regex1]
regex: <graphviz.files.Source at [^>]*>
replace: <graphviz.files.Source>

[regex2]
regex: CPU times: .*
replace: CPU times: CPUTIME

[regex3]
regex: Wall time: .*
replace: Wall time: WALLTIME

[regex4]
regex: .* per loop \(mean ± std. dev. of .* runs, .* loops each\)
replace: TIMEIT_REPORT
"""
    #tmp_fn = "_sanitise_cfg.cfg"
    #with open(tmp_fn, "w") as f:
    #    f.write(sanitiser)

    #cmd=f'py.test --nbval-sanitize-with {tmp_fn} '
    cmd=f'py.test '

    file_excludes = listify(file_excludes)

    for d in listify(dir_excludes):
        cmd = cmd + ' --ignore={} '.format(quote(d))
        print("*Not testing in directory: {}*".format(d))

    cmd = cmd+' --nbval '
    ## WARNING - TO DO - if we are running this from a notebook, also exclude path=='.'
    if path is None and filename is None:
        #Process current directory
        return cli_command(cmd)
    elif filename:
        #Process file(s) in directory
        if isinstance(filename, list):
            for _filename in filename:
                cmd = '{cmd} {filename}'.format(cmd=cmd, filename=pathmaker(path, quote(_filename)))
                resp=cli_command(cmd)
        else:
            cmd = '{cmd} {filename}'.format(cmd=cmd, filename=pathmaker(path, quote(filename)))
            resp=cli_command(cmd)
        return resp
    else:
        #Process files in path
        #If we pass a directory name in then the test will be run over all files in the directory
        #py.test accumulates the test responses
        resps = []
        for singlepath in listify(path):
            for dirname, subdirs, files in os.walk(singlepath):
                exclude_items(subdirs, dir_excludes)
                exclude_items(files, file_excludes, ipynb_only=True)
                print('Processing directory: {}'.format(dirname))
                with click.progressbar(files) as bar:
                    for filename in bar:
                        filepathname=os.path.join(dirname, filename)
                        cmd = '{cmd} {path}'.format(cmd=cmd, path=quote(filepathname))
                        resps.append( cli_command(cmd) )
        #for singlepath in listify(path):
        #    print("\nTesting in directory: {}".format(singlepath))
        #    if singlepath=='.':
        #        print('**DO NOT test in current directory from a notebook**')
        #    cmd = '{cmd} {path}'.format(cmd=cmd, path=quote(singlepath))
        #    resps.append( cli_command(cmd) )
        
        os.unlink(tmp_fn)
        return resps

def notebookProcessor(notebook, mode=None, outpath=None, outfile=None, inplace=True):
    ''' Clear notebook output cells.
    
        Process a single notebook, clearing cell outputs running cells until
        a warning, or running all cells despite warnings.
        
        Processed notebooks can be written to a specified directory or rendered inplace.
    '''
    
    if mode is None: return (-1, 'Mode not specified.')
    
    if outpath is not None and not os.path.exists(outpath):
        os.makedirs(outpath)
    
    if outfile is not None:
        outpath = '/'.join([outpath,outfile]) if outpath is not None else outfile
    
    cmd='jupyter nbconvert --to notebook'

    if mode in ['clearOutput', 'clearOutputTest' ]:
        cmd = '{cmd} --ClearOutputPreprocessor.enabled=True'.format(cmd=cmd)
    elif mode == 'run':
        cmd = '{cmd} --execute'.format(cmd=cmd)
    elif mode == 'runWithErrors':
        cmd = '{cmd} --ExecutePreprocessor.allow_errors=True --execute'.format(cmd=cmd)
    else: return (-1, 'Mode not specified correctly.')
    
    if outpath is None and inplace:
        cmd='{cmd} --inplace'.format(cmd=cmd)

    #Select file
    cmd='{cmd} {notebook}'.format(cmd=cmd,notebook=quote(notebook))
    
    #If output path not set, and --inplace is not set,
    #  nbformat will create a new file with same name ending: .nbformat.ipynb
    if outpath is not None:
        cmd ='{cmd} --output-dir {outpath}'.format(cmd=cmd, outpath=quote(outpath))
    #print(f"Trying command {cmd}")
    return cli_command(cmd)

def directoryProcessor(path,
                       mode=None, outpath=None, inplace=True,
                       include_hidden=False,
                       dir_excludes=None,
                       file_excludes=None, rmdir=False, currdir=False, subdirs=True,
                       reportlevel=1, logfile=None):
    ''' Process all the notebooks in one or more directories and
        (optionally) in associated subdirectories.
    
        Processed notebooks can be written to a specified directory or rendered inplace.
            
        Path hierarchies to notebooks in multiple directories or subdirectories are
        respected when writing to a specified output directory.
    '''
    
    def _process(outpath):
        ''' Process files associated with a particular directory '''
        processfiles=[f for f in files if f.endswith('.ipynb')]
        
        if subdirs:
            print(dirname)
            if outpath is not None:
                outpath='/'.join([outpath, dirname])
                if not os.path.exists(outpath):
                    os.makedirs(outpath)
        if not mode == 'tests':
            #print('About to process {}'.format(processfiles))
            with click.progressbar(processfiles) as bar:
                for filename in bar:
                    if not currdir and dirname=='.': continue
                    if reportlevel>1:
                        print("Processing >{}<".format('/'.join([dirname,filename])))
                    resp = notebookProcessor('/'.join([dirname,filename]), mode=mode, outpath=outpath, inplace=inplace )
                    if reportlevel>0 and resp and resp[0]!=0:
                        print("Error with {}".format('/'.join([dirname,filename])))
                    if logfile:
                        with open(logfile, "a") as out:
                            out.write(resp[1])

        #if mode in ['tests', 'clearOutputTest']:
        #    #Tests need to run in original dir in case of file dependencies
        #    testreport = notebookTest(path=dirname,dir_excludes=dir_excludes)
        #    print('tested:',dirname)
        #    print(testreport[1])
    
    #if mode == 'clearOutputTest':
    #    #If we are testing for warnings, need to test in original directory
    #    #  in case there are file dependencies
    #    outpath=None
    #    inplace=True
    
    if mode is None: return
    
    if isinstance(path, list):
        if rmdir:
            shutil.rmtree(outpath, ignore_errors=True)
            #Make sure we only delete the directory on the way in...
            rmdir=False
            
        for _path in path:
            #When provided with multiple directories, process each one separately
            #Note that subdirs for each directory can be handled automatically
            directoryProcessor(_path, mode, '/'.join([outpath, _path]), inplace,
                               include_hidden, dir_excludes, file_excludes,
                               rmdir, currdir, subdirs, reportlevel, logfile)
        return

    #TO DO - simplify this so we just pass one exclusion type then detect if file or dir?
    file_excludes = listify(file_excludes)
    dir_excludes = listify(dir_excludes)
    
    if outpath is not None and os.path.exists(outpath):
        if rmdir:
            print('\n***Deleting directory `{}` and all its contents....***\n\n'.format(outpath))
            shutil.rmtree(outpath, ignore_errors=True)
        else:
            print('\nOutput directory `{}` already exists. Remove it first by setting: rmdir=True\n'.format(outpath))
        
    #dir_excludes = [] if dir_excludes is None else dir_excludes 
    #file_excludes = [] if file_excludes is None else file_excludes
    if os.path.isfile(path):
        notebookProcessor(path, mode=mode, outpath=outpath, inplace=inplace )
    elif subdirs:
        for dirname, subdirs, files in os.walk(path):
            exclude_items(subdirs, dir_excludes, not include_hidden)
            exclude_items(files, file_excludes, not include_hidden)
            _process(outpath)
    # if passed a single file rather than directory path
    else:
        files=os.listdir(path)
        exclude_items(files, file_excludes, not include_hidden)
        dirname=path
        _process(outpath)

# Via Claude.ai
import tempfile
import warnings


def add_to_zipfile_with_warning(zf, filename, tmp_filename=None):
    try:
        # Temporarily set warnings to raise exceptions
        with warnings.catch_warnings():
            warnings.simplefilter("error", UserWarning)
            zf.write(filename, tmp_filename)
    except UserWarning as w:
        if "Duplicate name:" in str(w):
            print(f"Warning: Duplicate file in zip - {tmp_filename or filename}")
        else:
            # Re-raise other warnings
            raise


# via claude.ai
def process_notebook_with_temp_dir(filepathname, file_processor, zf):
    # Get the directory and filename of the notebook
    file_dir, filename = os.path.split(filepathname)

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy the original notebook to the temp directory
        temp_filepathname = os.path.join(temp_dir, filename)
        shutil.copy2(filepathname, temp_filepathname)

        if file_processor in ['clearOutput', 'runWithErrors'] and filename.endswith('.ipynb'):
            # Process the notebook in the temporary directory
            notebookProcessor(temp_filepathname, mode=file_processor, inplace=True)

        # Add the processed notebook to the zip file, preserving the original path
        # zf.write(temp_filepathname, filepathname)
        add_to_zipfile_with_warning(zf, temp_filepathname, filepathname)


def process_notebook_with_temp(filepathname, file_processor, zf):
    file_dir, filename = os.path.split(filepathname)

    # Create a temporary filename in the same directory
    with tempfile.NamedTemporaryFile(delete=False, dir=file_dir, suffix='.ipynb') as temp_file:
        temp_filepathname = temp_file.name
        try:
            # Copy the original notebook to the temporary filename
            shutil.copy2(filepathname, temp_filepathname)

            if file_processor in ['clearOutput', 'runWithErrors'] and filename.endswith('.ipynb'):
                # Process the notebook with the temporary filename
                notebookProcessor(temp_filepathname, mode=file_processor, inplace=True)

            # Add the processed notebook to the zip file, preserving the original path
            add_to_zipfile_with_warning(zf, temp_filepathname, filepathname)

        finally:
            # Ensure the temporary file is deleted after processing
            if os.path.exists(temp_filepathname):
                os.remove(temp_filepathname)

# Running zipper with a file_processor will change the cell state in current dir
# That is, notebooks are processed in place then zipped
# The notebooks as seen in the dir will reflect those in the zipfile
# We could modify this behaviour so it does not affect original notebooks?
def zipper(dirtozip, zipfilename,
           include_hidden=False,
           dir_excludes=None,
           file_excludes=None, 
           file_processor=None,
           reportlevel=1, rmdir=False, 
           zip_append=False):
    ''' Zip the contents of a directory and its subdirectories '''

    file_excludes = listify(file_excludes)
    dir_excludes = listify(dir_excludes)

    zip_permission = "a" if zip_append else "w"
    # Create a new/replacement zip file, rather than append if zipfile already exists
    zf = zipfile.ZipFile(zipfilename, zip_permission, compression=zipfile.ZIP_DEFLATED)

    # Don't zip files of same name as the zip file we are creating
    file_excludes.append(zipfilename)
    # if we have just a single file to zip and not a dir, zip that
    if os.path.isfile(dirtozip):
        if file_processor in [
            "clearOutput",
            "clearOutputTest",
            "runWithErrors",
        ] and dirtozip.endswith(".ipynb"):
            process_notebook_with_temp(dirtozip, file_processor, zf)
        # print("command is run, should be zipping now")
        else:
            zf.write(dirtozip)
    elif os.path.isdir(dirtozip):
        # https://stackoverflow.com/a/31779538/454773
        for dirname, subdirs, files in os.walk(dirtozip):
            exclude_items(subdirs, dir_excludes, not include_hidden)
            exclude_items(files, file_excludes, not include_hidden)
            print('Processing directory: {}'.format(dirname))
            zf.write(dirname)
            with click.progressbar(files) as bar:
                for filename in bar:
                    if reportlevel>1:print(filename)
                    filepathname=os.path.join(dirname, filename)
                    # There is no point using 'run': if there is an error, nbconvert will fail
                    if file_processor in ['clearOutput', 'runWithErrors'] and filename.endswith('.ipynb'):
                        # This introduces side effects - notebooks are processed in current path
                        process_notebook_with_temp(filepathname, file_processor, zf)
                        # notebookProcessor(filepathname, mode=file_processor, inplace=True)
                    else:
                        zf.write(filepathname)
    zf.close()

    # Is this too risky?!
    # if rmdir: shutil.rmtree(dirtozip, ignore_errors=True)
    return zipfilename

def insideZip(zfn, report=True):
    ''' Look inside a zip file.
        The report contains four columns: file_size, file compressed size, datetime and filename.
        Setting report=True returns a pretty printed report. '''
    if not os.path.isfile(zfn):
        print("\nHmm... {} doesn't seem to be a file?\n".format(zfn))
        return
    print('\nLooking inside zipfile: {}\n'.format(zfn))
    fz=zipfile.ZipFile(zfn)
    
    txt=[]
    for fn in fz.infolist():
        txt.append( [fn.file_size,
                     fn.compress_size,
                     datetime.datetime(*fn.date_time).isoformat(),
                     fn.filename] )
        print('{}, {}, {}, {}'.format(fn.file_size,
                     fn.compress_size,
                     datetime.datetime(*fn.date_time).isoformat(),
                     fn.filename))
    tabulate(txt, headers=['Full','Zip','Datetime','Path'],tablefmt="simple")
    return txt  


@click.command()
@click.option(
    "--file-processor", "-r", type=click.Choice(["clearOutput", "runWithErrors"])
)
@click.option("--include-hiddenfiles", "-H", is_flag=True, help="Include hidden files")
@click.option(
    "--exclude-dir",
    "-X",
    multiple=True,
    type=click.Path(resolve_path=False),
    help="Exclude specified directory",
)
@click.option(
    "--exclude-file",
    "-x",
    multiple=True,
    type=click.Path(resolve_path=False),
    help="Exclude specified file",
)
@click.option("--zip_append", "-a", is_flag=True, help="Add to existing zip file")
@click.option("--force", "-F", is_flag=True, default=False, help="Force the operation.")
@click.argument(
    "path", type=click.Path(resolve_path=False)
)  
# @click.argument('zipfile', type=click.File('wb'))
@click.argument("zipfile", type=click.Path())
def cli_zip(file_processor, include_hiddenfiles, exclude_dir, exclude_file, zip_append, force, path, zipfile):
    """Create a zip file from the contents of a specified directory.
    
    The zipper can optionally run a notebook processor on notebooks before zipping them to check that all cells are run or all cells are cleared.
    """
    print('You must be crazy using this...')

    if not zip_append and not force:
        print(f"\nThis would overwrite any previous {zipfile} file\n\tUse -F/--force to overwrite.\n\tUse -a, --zip_append to add to an existing zip file.")
        exit(-1)
    elif force and not zip_append:
        print(f"Deleting/completely overwriting {zipfile}")
    else:
        print(f"\nAppending zipped files to: {zipfile}\n")

    fn = zipper(path, zipfile,
                include_hidden=include_hiddenfiles,
                dir_excludes=exclude_dir,
                file_excludes=exclude_file, 
                file_processor=file_processor,
                zip_append=zip_append)

    print(f"\nZip file: {fn}\n")


# h/t Claude.ai
@click.command()
@click.argument("zipfile_path", type=click.Path(exists=True))
@click.argument("target_dir", type=click.Path(), default="zip_output")
def cli_unzip(zipfile_path, target_dir):
    """
    Unzip a file into a target directory.

    ZIPFILE_PATH: Path to the zip file to be extracted.
    TARGET_DIR: Directory to extract the contents to (default: zip_output).
    """
    try:
        # Ensure the target directory exists
        os.makedirs(target_dir, exist_ok=True)

        # Open and extract the zip file
        with zipfile.ZipFile(zipfile_path, "r") as zip_ref:
            zip_ref.extractall(target_dir)

        click.echo(f"Successfully extracted {zipfile_path} to {target_dir}")
    except zipfile.BadZipFile:
        click.echo(f"Error: {zipfile_path} is not a valid zip file", err=True)
    except PermissionError:
        click.echo(
            f"Error: Permission denied when trying to extract to {target_dir}", err=True
        )
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)


@click.command()
@click.option("--quiet", "-q", is_flag=True, help="Suppress the report.")
@click.option("--warnings", "-w", is_flag=True, help="Display warnings")
@click.argument("filename", type=click.Path(resolve_path=True), nargs=-1)
def cli_zipview(filename, warnings, quiet):
    """List the contents of one or more specified zipfiles.
    """
    zip_contents = []
    for f in listify(filename):
        zip_contents.append((f, insideZip(f)))

    if warnings and zip_contents:
        for (zn, item) in zip_contents:
            print(f"\n\n====== Zip file quality report: {zn} ======\n")
            for record in item:
                if record[1] > 1e6:
                    print(f"WARNING: \"{record[3]}\" looks quite large file ({humanize.naturalsize(record[0])} unzipped, {humanize.naturalsize(record[1])} compressed)")
                for _path in record[3].split('/'):
                    if len(_path) > 50:
                        print(f"ERROR: the filepath element \"{_path}\" in \"{record[3]}\" is too long (max. 50 chars)")
                    if _path.startswith("."):
                        print(f"WARNING: \"{record[3]}\" is a hidden file/directory (do you really need it in the zip file?)")
        print("\n===========================\n\n")

def _notebookTest(testitems,  outfile=None, dir_excludes=None, file_excludes=None):
    path=[]
    filename=[]
    
    for i in listify(testitems):
        if os.path.isdir(i):
            path.append(i)
        else:
            filename.append(i)
    resps = notebookTest(path=path, filename=filename, dir_excludes=dir_excludes, file_excludes=file_excludes)
    if isinstance(resps, tuple): resps = [resps]
    
    for resp in resps:
        if outfile:
            with open(outfile, "a") as out:
                out.write(resp[1])
            print('\nTest report written to {}'.format(outfile))
        else:
            print(resp[1])


@click.command()
@click.option('--exclude-dir','-X', multiple=True,type=click.Path(resolve_path=False), help='Do not recurse through specified directory when assembling tests.')
@click.option('--exclude-file','-x', multiple=True,type=click.Path(resolve_path=False), help='Exclude specified file')
@click.option('--outfile','-o', type=click.Path(resolve_path=False), help='Output report file. Leave this blank to display report on command line.')
@click.argument('testitems', type=click.Path(resolve_path=False),nargs=-1)
def cli_nbtest( exclude_dir, exclude_file, outfile, testitems):
    """Test specified notebooks and/or the notebooks in a specified directory or directories (`TESTITEMS`) using the `nbdime` plugin for `py.test`.
    
    Running `tm351nbtest` without any specified directory or file will assemble tests recursively from the current directory down."""
    testitems = testitems or '.'
    _notebookTest(testitems, outfile, exclude_dir, exclude_file)


@click.command()
@click.option('--file-processor','-r', type=click.Choice(['clearOutput', 'runWithErrors']), help='File processor actions that can be applied to notebooks using `nbconvert`')
@click.option('--outpath', '-O', type=click.Path(resolve_path=False), help='path to output directory')
@click.option('--inplace/--no-inplace',default=True, help='Run processors on notebooks inplace')
@click.option('--exclude-dir', '-X', multiple=True, type=click.Path(resolve_path=False), help='Exclude specified directory')
@click.option('--exclude-file','-x', multiple=True,type=click.Path(resolve_path=False), help='Exclude specified file')
@click.option('--include-hidden/--no-include-hidden',default=False, help='Include hidden files')
@click.option('--rmdir/--no-rmdir',default=False, help='Check the output directory is empty before we use it')
@click.option('--currdir/--no-currdir',default=False, help='Process files in current directory')
@click.option('--subdirs/--no-subdirs',default=True, help='Process files in subdirectories')
@click.option('--reportlevel', default=1, help='Reporting level')
@click.argument('path',type=click.Path(resolve_path=False))
def cli_nbrun(file_processor, outpath, inplace, exclude_dir, exclude_file, include_hidden, rmdir, currdir, subdirs, reportlevel, path):
    """Directory processor for notebooks - allows the user to run nbconvert operations on notebooks, such as running all cells or clearing all cells.
    
    To run tests, use: tm351nbtest
    
    To zip folders (with the option or running notebook processors on zipped files), use: tm351zip
    """
    directoryProcessor(path,
                       mode=file_processor, outpath=outpath, inplace=inplace,
                       include_hidden=include_hidden,
                       dir_excludes=exclude_dir,
                       file_excludes=exclude_file, rmdir=rmdir, currdir=currdir,
                       subdirs=subdirs,reportlevel=reportlevel)


from github import Github
import getpass

import base64
import logging
from github.GithubException import GithubException

def get_sha_for_tag(repository, tag):
    """
    Returns a commit PyGithub object for the specified repository and tag.
    """
    branches = repository.get_branches()
    matched_branches = [match for match in branches if match.name == tag]
    if matched_branches:
        return matched_branches[0].commit.sha

    tags = repository.get_tags()
    matched_tags = [match for match in tags if match.name == tag]
    if not matched_tags:
        raise ValueError('No Tag or Branch exists with that name')
    return matched_tags[0].commit.sha

def download_directory(repository, sha, server_path, outpath='gh_downloads', file_processor=None):
    """
    Download all contents at server_path with commit tag sha in
    the repository.
    """
    contents = repository.get_dir_contents(server_path, ref=sha)
    if not os.path.exists(outpath):
        os.makedirs(outpath)
            
    for content in contents:
        print("Downloading: %s" % content.path)
        if content.type == 'dir':
            download_directory(repository, sha, content.path, '/'.join([outpath,content.name]))
        else:
            try:
                path = content.path
                file_content = repository.get_contents(path, ref=sha)
                file_data = base64.b64decode(file_content.content)
                outpathfile='/'.join([outpath,content.name])
                file_out = open(outpathfile, "wb")
                file_out.write(file_data)
                file_out.close()
            except (IOError, github.GithubException) as exc:
                #If we fail over because of a large blog, use the data api for the download
                ret,error=exc.args
                if 'message' in error and error['message']=='Not Found':
                    print('Hmm... file not found? {}'.format(path))
                elif 'errors' in error and error['errors'][0]['code']=='too_large':
                    #print('...large file, trying blob download instead...')
                    file_content = repository.get_git_blob(content.sha)
                    file_data = base64.b64decode(file_content.content)
                    file_out = open('/'.join([outpath,content.name]), "wb")
                    file_out.write(file_data)
                    file_out.close()
                #logging.error('Error processing %s: %s', content.path, exc)
            #if content.name.endswith('.ipynb') and file_processor in ['clearOutput', 'clearOutputTest','runWithErrors' ]:
            #        notebookProcessor(outpathfile, file_processor)


def github_repo_branches(repository):
    return [br.name for br in repository.get_branches()]

def github_repo_topdirs(contents):
    return [i.name for i in contents if i.type=='dir']

DEFAULT_REPO='undercertainty/tm351'

@click.command()
@click.option('--github-user', '-u',  help="Your Github username.")
@click.option('--password', hide_input=True,
              confirmation_prompt=False)
@click.option('--repo','-r', prompt='Repository ({})'.format(DEFAULT_REPO),
              help='Repository name')
@click.option('--branch','-b',help='Branch or tag to download')
@click.option('--directory', help='Directory to download (or: all)')
@click.option('--savedir',type=click.Path(resolve_path=False),
              help='Directory to download repo / repo dir into; default is dir name')
@click.option('--file-processor', type=click.Choice(['clearOutput', 'runWithErrors']), help='Optionally specify a file processor to be run against downloaded notebooks.')
@click.option('--zip/--no-zip', default=False, help='Optionally create a zip file of the downloaded repository/directory with the same name as the repository/directory.')
@click.option('--auth/--no-auth', default=True, help="By default, run with auth (prompt for credentials)")
@click.option('--with-tests','-t',is_flag=True, help="Run tests on notebooks after download")
@click.option('--logfile',type=click.Path(resolve_path=False), help='Path to logfile')
def cli_gitrepos(github_user, password, repo, branch, directory, savedir, file_processor, zip, auth, with_tests, logfile):
    """Download files from a specified branch in a particular git repository.
    
    The download can also be limited to just the contents of a specified directory.
    
    Don't worry that there look to be a lot of arguments - you will be prompted for them if you just run: tm351gitrepos
    """
    
    if auth or github_user:
        if not github_user: github_user = click.prompt('\nGithub username')
        if not password: password = click.prompt('\nGithub password', hide_input=True)
        github = Github(github_user, password)
        #Show we're keeping no password...
        password = None
        auth = True
    else: github = Github()


    if auth:
        user = github.get_user()
        #organisations = github.get_user().get_orgs()
        print('Logging into git as {} ({})'.format(github_user, user.name))
    
    repo = repo or DEFAULT_REPO
    repository = github.get_repo(repo)

    if not branch:
        print('\nBranches available:\n\t{}'.format('\n\t'.join(github_repo_branches(repository)) ))
        branch = click.prompt('\nWhich branch? (master)')

    branch_or_tag_to_download = branch or 'master'
    sha = get_sha_for_tag(repository, branch_or_tag_to_download)
    
    another = ''
    while another!='-':
        if not directory:
            if branch!='master':
                contents = repository.get_dir_contents('.', ref=sha)
            else:
                contents = repository.get_dir_contents('.')
            print('\nYou can download all directories from this repo (all) or select one:\n\t{}'.format('\n\t'.join(github_repo_topdirs(contents))))
            directory = click.prompt('Which directory? (all)')

        directory_to_download = '.' if (not directory or directory=='all') else directory
        outpath = savedir or directory_to_download
        if outpath == '.' and savedir !='.': outpath=repo.replace('/','_')+'_files'
        
        msg='\nOkay... downloading {}/{}'.format(repo,directory_to_download ) 
        if file_processor is not None:
            msg = msg + ' using notebook processor: {}'.format(file_processor)
        else: msg = msg + ' with no notebook processing'
        print(msg)
        download_directory(repository, sha, directory_to_download, outpath,file_processor )

        if file_processor in ['clearOutput', 'clearOutputTest','runWithErrors' ]:
            click.echo('\nRunning notebook processor: {}'.format(file_processor))
            directoryProcessor(outpath, mode=file_processor, subdirs=True,
                                reportlevel=1, logfile=logfile)
            if logfile:
                click.echo('\nLog written to {}'.format(logfile))

        if with_tests:
            click.echo('\nRunning notebook tests over: {}'.format(outpath))
            if not logfile: logfile = 'tests.log'
            _notebookTest(outpath, logfile )
            click.echo('\nLog written to {}'.format(logfile))
            
        if zip:
            print('\nZipping into: {}/nYou may also want to delete the working directory ({}).'.format(repository, outpath) )
            zipper(outpath,repository)
        else:
            print('\n\nTo zip the downloaded directory, run something like: {}'.format('tm351zip {o} {z}\n\nTo run a notebook processor (OPTIONS: runWithErrors, clearOutput) while zipping: tm351zip "{o}" {z} --file-processor OPTION\n'.format(o=outpath,z=repository.name)))

        directory=''
        another = click.prompt('\Download another directory from this branch? (To quit: -)')

     #TODO
     #print('\n\nTo run this command again: {}'.format())
