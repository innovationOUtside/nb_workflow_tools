from setuptools import setup

setup(
    name="tm351-nb-utils",
    version="0.0.14",
    py_modules=["tm351_nb_utils", "updaters", "html2nb", "splitmerge", "collapser"],
    packages=["ou_nb_workflow_tools"],
    install_requires=[
        "Click",
        "tabulate",
        "pytest",
        "nbval",
        "PyGithub",
        "beautifulsoup4",
        "humanize",
    ],
    entry_points="""
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
        nb_collapse_tagstoolbar = ou_nb_workflow_tools.tags_collapser:tag_toolbar_collapser
        nb_image_table = ou_nb_workflow_tools.cli:imagetable_generate
        nb_cell_metadata_strip = ou_nb_workflow_tools.metadata_cleaner:cell_metadata_key_cleaner
        nb_cell_figure_tagger = ou_nb_workflow_tools.figure_cell_autotagger:figure_autotagger
        nb_cell_separator_fixer = ou_nb_workflow_tools.separator_fixer:separator_cleaner
   """,
)
