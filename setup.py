# -*- coding: utf-8 -*-

LONG_DESCRIPTION = \
'''
This package contains the tikz Sphinx extension, which enables the use
of the PGF/TikZ LaTeX package to draw nice pictures.
'''

NAME         = 'sphinxcontrib-tikz'
DESCRIPTION  = 'TikZ extension for Sphinx'
VERSION      = '0.4.14'
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
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Documentation',
    'Topic :: Utilities',
    ]

if __name__ == "__main__":

    from setuptools import setup, find_packages
    import sys

    # Use 2to3 for Python 3 without warnings in Python 2
    extra = {}
    if sys.version_info >= (3,):
        extra['use_2to3'] = True

    setup(
        name=NAME,
        version=VERSION,
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
        **extra
        )
