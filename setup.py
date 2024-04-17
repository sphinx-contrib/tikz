# -*- coding: utf-8 -*-

import pathlib

def get_version(path : str = 'sphinxcontrib/__init__.py') -> str:
    """
    Get the version string, written as "__version__ = <version-comes-here>".

    Inspired by https://packaging.python.org/en/latest/guides/single-sourcing-package-version/.
    """
    with open(pathlib.Path(__file__).parent / path) as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('__version__')[-1].strip().lstrip('=').strip()
    raise RuntimeError("Unable to find version string.")

LONG_DESCRIPTION = \
'''
This package contains the tikz Sphinx extension, which enables the use
of the PGF/TikZ LaTeX package to draw nice pictures.
'''

NAME         = 'sphinxcontrib-tikz'
DESCRIPTION  = 'TikZ extension for Sphinx'
AUTHOR       = 'Christoph Reller'
AUTHOR_EMAIL = 'christoph.reller@gmail.com'
URL          = 'https://bitbucket.org/philexander/tikz'
DOWNLOAD     = 'http://pypi.python.org/pypi/sphinxcontrib-tikz'
LICENSE      = 'BSD'
REQUIRES     = ['Sphinx']
CLASSIFIERS  = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Topic :: Documentation',
    'Topic :: Utilities',
    ]

if __name__ == "__main__":

    from setuptools import setup, find_packages

    setup(
        name=NAME,
        version = get_version(),
        url=URL,
        download_url=DOWNLOAD,
        license=LICENSE,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        zip_safe=False,
        classifiers=CLASSIFIERS,
        platforms='any',
        packages=find_packages(),
        include_package_data=True,
        install_requires=REQUIRES,
        namespace_packages=['sphinxcontrib'],
    )
