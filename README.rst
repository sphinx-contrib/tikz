==============================================
Description of the Ti\ *k*\ Z Sphinx Extension
==============================================

This extension to `Sphinx <http://sphinx.pocoo.org/>`__ enables the use of the
PGF/Ti\ *k*\ Z LaTeX package to draw nice pictures.  (See `CTAN
<http://www.ctan.org/tex-archive/graphics/pgf/>`__ or `sourceforge
<http://sourceforge.net/projects/pgf/>`__; the manual is, e.g., `here
<http://www.ctan.org/tex-archive/graphics/pgf/base/doc/generic/pgf/pgfmanual.pdf>`__.
Also have a look at contributions such as `pgfplots
<http://www.ctan.org/tex-archive/graphics/pgf/contrib/pgfplots/>`__.)

Use the extension at your own risk.  Anything might change in future versions
without further notice.

----

:Version: 0.4.1
:Author: Christoph Reller ``christoph.reller@gmail.com``
:License: `BSD License <http://opensource.org/licenses/bsd-license.html>`__
:Download: `tikz.py <http://people.ee.ethz.ch/~creller/web/_static/tikz.py>`__
:Git Repository: https://bitbucket.org/philexander/tikz
:PyPI Package: http://pypi.python.org/pypi/sphinxcontrib-tikz

Prerequisites and Configuration
===============================

Prerequisites
-------------

On your computer the following must be installed:

* ``latex`` with the ``tikz`` and the ``amsmath`` packages
* ``pdftoppm`` (part of the Poppler pdf library)
* either of the following:

  - ``pnmcrop`` and ``pnmtopng`` (both part of the Netpbm package)
  - ``convert`` (part of the ImageMagick package)

(We cannot use ``dvipng`` as the ``pngmath`` Sphinx extension does because there
is an issue with cropping the image if postscript specials are used.)

For **Ubuntu Linux** you roughly have to have the following packages installed:

* ``texlive`` and ``texlive-pictures`` (and maybe more LaTeX packages)
* ``poppler-utils``
* ``netpbm`` or ``imagemagick``

For **Mac OS X** a possible way of getting this extension working is:

* Install `homebrew <http://mxcl.github.com/homebrew/>`__ in the terminal by::

    /usr/bin/ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"

* Install ``poppler`` (``pdftoppm`` comes with it), by::
    
    brew install poppler

Configuration
-------------

If you have installed the Ti\ *k*\ z Sphinx extension e.g. using `PyPI
<http://pypi.python.org/pypi/sphinxcontrib-tikz>`__, then you have to load the
extension in the Sphinx project configuration file ``conf.py`` by::
 
  extensions = ['sphinxcontrib.tikz']

Also in ``conf.py``, you have to specify the LaTeX preamble in the
``latex_elements`` dictionary as::

  latex_elements = {
  ‹...›
  'preamble': '\\usepackage{tikz}',
  ‹...›
  }

Additionally, the following configuration values are supported for the ``html``
build target:

* Choose the image processing ``‹suite›``, either ``'Netpbm'`` or
  ``'ImageMagick'`` (``'Netpbm'`` by default)::

    tikz_proc_suite = ‹suite›

* Enable/disable transparent graphics (enabled by default)::

    tikz_transparent = ‹True or False›

* Add ``‹string›`` to the LaTeX preamble::

    tikz_latex_preamble = ‹string›

* Add ``\usetikzlibrary{‹string›}`` to the LaTeX preamble::

    tikz_tikzlibraries = ‹string›

.. note:: The above configuration values only apply to the ``html`` build
   target.  If you want to use the ``latex`` target, then you have to take care
   to include in the preamble for the ``latex`` target:
   
   * The ``tikz_latex_preamble``
   * The ``tikz_libraries``
   * Any ``‹tikz libraries›`` given to the ``libs`` option of the ``tikz``
     directive (see :ref:`usage`)

   This can be done, e.g., as::

     latex_elements = {
     ‹...›
     'preamble': '''\usepackage{tikz}''' + '''
     \usetikzlibrary{''' + tikz_tikzlibraries + ‹tikz libraries› + '''}'''
     ‹...›
     }

.. note:: If you want to make use of the Ti\ *k*\ Z externalization library for
   the LaTeX build output, then you may want to change the line::

     LATEXOPTS =
     
   in ``/usr/share/sphinx/texinputs/Makefile`` to::

     LATEXOPTS = "-shell-escape"

.. highlight:: rest

.. _usage:

Usage
=====

The extension adds a ``tikz``-directive and a ``tikz``-role.  The usage is very
similar to the standard math Sphinx extensions.

The **tikz-directive** can be used in two ways::

  .. tikz:: ‹tikz code, potentially broken
     across lines›
     :libs: ‹tikz libraries›
     :stringsubst:

or::

  .. tikz:: ‹caption, potentially broken
     across lines›
     :libs: ‹tikz libraries›
     :stringsubst:

     ‹tikz code, potentially broken
     across lines›

The ``‹caption›`` is optional, but if present it is printed as a picture caption
below the picture.

The ``:libs:`` option expects its argument ``‹tikz libraries›`` to be a comma
separated list of tikz libraries to use.  If you want to build the LaTeX target
then make sure that you add these libraries to ``latex_preamble`` in
``conf.py``.

The ``stringsubst`` option enables the following string substitution in the
``‹tikz code›``.  Before processing the ``‹tikz code›`` the string ``%(wd)s`` is
replaced by the project root directory.  This is convenient when referring to
some source file in the LaTeX code.

The ``‹tikz code›`` is code according to the tikz LaTeX package.  It behaves as
if inside a ``tikzpicture`` environment.

The **tikz-role** is used as follows::

  :tikz:`‹tikz code›`

The ``‹tikz code›`` is code according to the tikz LaTeX package.  It behaves as
if inside a ``\tikz`` macro.  Ti\ *k*\ Z options can be given at the start of
the ``‹tikz code›``.

Examples
========

.. note:: These examples only render in a Sphinx project with a proper
	  configuration of the Ti\ *k*\ z Sphinx extension.

::

  .. tikz:: [>=latex',dotted,thick] \draw[->] (0,0) -- (1,1) -- (1,0)
     -- (2,0);
     :libs: arrows


.. tikz:: [>=latex',dotted,thick] \draw[->] (0,0) -- (1,1) -- (1,0)
   -- (2,0);
   :libs: arrows

::

  .. tikz:: An Example Directive with Caption

     \draw[thick,rounded corners=8pt]
     (0,0)--(0,2)--(1,3.25)--(2,2)--(2,0)--(0,2)--(2,2)--(0,0)--(2,0);

.. tikz:: An Example Directive with Caption

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
a caption then the LaTeX target built by the sphinx builder will not compile.
This is because, as soon as you specify a caption, the ``tikzpicture``
environment is set inside a ``figure`` environment and hence it is a float.

If you enable ``:stringsubst:`` then the character ``%`` cannot be used anymore
for commenting LaTeX code.
