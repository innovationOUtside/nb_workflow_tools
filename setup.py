from setuptools import setup

setup(
    name="tm351_nb_utils",
    version='0.0.2',
    py_modules=['tm351_nb_utils'],
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
    ''',
)