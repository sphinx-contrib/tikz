==============================================
 Description of the ``tikz`` Sphinx Extension
==============================================

This extension to `Sphinx <http://sphinx.pocoo.org/>`__ enables the use of the
PGF/TikZ LaTeX package to draw nice pictures.  (See `CTAN
<http://www.ctan.org/tex-archive/graphics/pgf/>`__ or `sourceforge
<http://sourceforge.net/projects/pgf/>`__; the manual is, e.g., `here
<http://www.ctan.org/tex-archive/graphics/pgf/base/doc/generic/pgf/pgfmanual.pdf>`__.)
Have also a look at contributions such as `pgfplots
<http://www.ctan.org/tex-archive/graphics/pgf/contrib/pgfplots/>`__.

Use the extension at your own risk.  Anything might change in future versions
without further notice.

----

:Version: 0.4
:Author: Christoph Reller ``creller@ee.ethz.ch``
:Download: `tikz.py <../_static/tikz.py>`__
:License: `BSD License <http://opensource.org/licenses/bsd-license.html>`__

Prerequisites and Configuration
===============================

On your computer the following must be installed:

* ``latex`` with the ``tikz`` and the ``amsmath`` packages
* ``pdftoppm`` (part of the Poppler pdf library)
* either of the following:

  - ``pnmcrop`` and ``pnmtopng`` (both part of the Netpbm package)
  - ``convert`` (part of the ImageMagick package)

(We cannot use ``dvipng`` as the math Sphinx extensions do because there is an
issue with cropping the image if postscript specials are used.)

The ``tikz`` Sphinx extension consists of the single file ``tikz.py`` (along
with this description).

In the Sphinx project configuration file ``conf.py`` you need to:

- add the directory where ``tikz.py`` is located to ``sys.path``, e.g. by::

    sys.path.append(os.path.expanduser('~/‹path to directory›'))

- load the extension by::

    extensions = ['tikz']

The following configuration values are supported:

* Choose the image processing ``‹suite›``, either ``'Netpbm'`` or
  ``'ImageMagick'`` (``'Netpbm'`` by default)::

    tikz_proc_suite = ‹suite›

* Enable/disable transparent graphics (enabled by default)::

    tikz_transparent = ‹True or False›

* Add ``‹string›`` to the latex preamble::

    tikz_latex_preamble = ‹string›

* Add ``\usetikzlibrary{‹string›}`` to the latex preamble::

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

The extension adds a ``tikz``-directive and a ``tikz``-role.  

The **tikz-directive** is used as follows::

  .. tikz:: ‹caption potentially broken
     across lines›
     :libs: ‹tikz libraries›

     ‹tikz code›

The caption is optional, but if present it is printed as a picture caption
centered below the picture.

The ``‹tikz libraries›`` option is a comma separated list of tikz libraries to
use.  If you want to build latex code then make sure that you add these to
``latex_preamble`` in ``conf.py``.

The ``‹tikz code›`` is code according to the tikz latex package.  It behaves as
if inside a ``tikzpicture`` environment with one enhancement: The string
``%(wd)s`` will be replaced by the project root directory.  This is convenient
when referring to some source file in the LaTeX code.

Note that there must be an empty line in front of ``‹tikz code›``.

The **tikz-role** is used as follows::

  :tikz:`‹tikz code›`

The ``‹tikz code›`` is code according to the tikz latex package.  It behaves as
if inside a ``\tikz`` macro.  TikZ options can be given at the start of the
``‹tikz code›``.

Examples
========

::

  .. tikz:: An example directive

     \draw[thick,rounded corners=8pt]
     (0,0)--(0,2)--(1,3.25)--(2,2)--(2,0)--(0,2)--(2,2)--(0,0)--(2,0);

.. tikz:: An example directive

   \draw[thick,rounded corners=8pt]
   (0,0)--(0,2)--(1,3.25)--(2,2)--(2,0)--(0,2)--(2,2)--(0,0)--(2,0);

::

  An example role :tikz:`[thick] \node[draw] (a) {A}; 
  \node[draw,dotted,right of=a] {B} edge[<-] (a);`


An example role :tikz:`[thick] \node[draw] (a) {A}; \node[draw,dotted,right
of=a] {B} edge[<-] (a);`

Caveats
=======

If you use the ``tikz`` directive inside of a table or a sidebar and you specify
a caption then the latex target built by the sphinx builder will not compile.
This is because, as soon as you specify a caption, the ``tikzpicture``
environment is set inside a ``figure`` environment and hence it is a float.
