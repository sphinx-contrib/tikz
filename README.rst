==============================================
 Description of the ``tikz`` Sphinx extension
==============================================

This extension to `Sphinx <http://sphinx.pocoo.org/>`_ enables the use of the
`PGF/TikZ LaTeX package
<http://www.ctan.org/tex-archive/graphics/pgf/base/doc/generic/pgf/pgfmanual.pdf>`_
to draw nice pictures.

----

:Version: 0.2
:Author: Christoph Reller ``creller@ee.ethz.ch``

Prerequisites and Configuration
===============================

On your computer the following must be installed:

* ``latex`` with the ``tikz`` and the ``amsmath`` packages
* ``pdftoppm`` (part of the Poppler pdf library)
* ``pnmcrop`` and ``pnmtopng`` (both part of the Netpbm package)

(We don't use ``dvipng`` as the math Sphinx extensions do because
there is an issue with cropping the image if postscript specials are used.)

The ``tikz`` Sphinx extension consists of the single file ``tikz.py`` (along
with this README file).

In the Sphinx project configuration file ``conf.py`` you need to:

- add the directory where ``tikz.py`` is located to ``sys.path``, e.g. by::

    sys.path.append(os.path.expanduser('~/‹path to directory›'))

- load the extension by::

    extensions = ['tikz']

The following configuration values are supported:

* To enable/disable transparent graphics (enabled by default)::

    tikz_transparent = ‹True or False›

* To add ``‹string›`` to the latex preamble::

    tikz_latex_preamble = ‹string›

* To add ``\usetikzlibrary{‹string›}`` to the latex preamble::

    tikz_tikzlibraries = ‹string›

  You might want to add the ``tikzlibraries`` in the ``latex_preamble``
  e.g. as::

    latex_preamble = '''
    ‹...›
    \usepackage{tikz}
    \usetikzlibrary{''' + tikz_tikzlibraries + '''}
    ‹...›
    '''

Usage
=====

The extension adds a ``tikz``-directive which is used as follows::

  .. tikz:: ‹caption potentially broken
     across lines›
     :libs: ‹tikz libraries›

     ‹tikz code›

The caption is optional, but if present it is printed as a picture caption
centered below the picture.

The ``‹tikz libraries›`` option is a comma separated list of tikz libraries to
use.  If you want to build latex code then make sure that you add these to
``latex_preamble`` in ``conf.py``.

The ``‹tikz code›`` finally is code according to the tikz latex package.  It
behaves as if inside a ``tikzpicture`` environment.  Note that there must be an
empty line in front of ``‹tikz code›``.

Examples
========

::

  .. tikz:: A Simple Example

     \draw[thick,rounded corners=8pt]
     (0,0)--(0,2)--(1,3.25)--(2,2)--(2,0)--(0,2)--(2,2)--(0,0)--(2,0);

Caveats
=======

If you use the ``tikz`` directive inside of a table or a sidebar and you specify
a caption then the latex target built by the sphinx builder will not compile.
This is because, as soon as you specify a caption, the ``tikzpicture``
environment is set inside a ``figure`` environment and hence it is a float.
