from setuptools import setup

setup(
    name="tm351-nb-utils",
    version='0.0.5',
    py_modules=['tm351_nb_utils', 'updaters', 'html2nb', 'splitmerge', 'collapser'],
    install_requires=[
        'Click',
        'tabulate',
        'pytest',
        'nbval',
        'PyGithub'
    ],
    entry_points='''
        [console_scripts]
        tm351zip=tm351_nb_utils:cli_zip
        tm351zipview=tm351_nb_utils:cli_zipview
        tm351gitrepos=tm351_nb_utils:cli_gitrepos
        tm351nbtest=tm351_nb_utils:cli_nbtest
        tm351nbrun=tm351_nb_utils:cli_nbrun
        upgrade_empinken_tags = updaters:upgrade_empinken_tags
        html2ipynb = html2nb:html2ipynb
        nb_merge = splitmerge:nb_merger
        nb_split = splitmerge:nb_splitter
        nb_collapse_activities = collapser:activity_collapser
    ''',
)