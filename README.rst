==============================================
Description of the Ti\ *k*\ Z Sphinx Extension
==============================================

This extension to `Sphinx <http://www.sphinx-doc.org>`__ enables the use of the
PGF/Ti\ *k*\ Z LaTeX package to draw nice pictures.  (See `CTAN
<http://www.ctan.org/tex-archive/graphics/pgf/>`__ or `sourceforge
<http://sourceforge.net/projects/pgf/>`__; the manual is, e.g., `here
<http://mirrors.ctan.org/graphics/pgf/base/doc/pgfmanual.pdf>`__.
Also have a look at contributions such as `pgfplots
<http://www.ctan.org/tex-archive/graphics/pgf/contrib/pgfplots/>`__.)

Use the extension at your own risk.  Anything might change in future versions
without further notice.

----

:Version: 0.4.14
:Author: Christoph Reller ``christoph.reller@gmail.com``
:License: `BSD License <http://opensource.org/licenses/bsd-license.html>`__
:Git Repository: https://bitbucket.org/philexander/tikz
:PyPI Package: http://pypi.python.org/pypi/sphinxcontrib-tikz
:Documentation: http://sphinxcontrib-tikz.readthedocs.io

Prerequisites and Configuration
===============================

Prerequisites
-------------

This extension relies on two software packages being installed on your computer:

A. ``latex`` with the ``tikz`` and the ``amsmath`` packages
B. A software package that is able to convert a PDF to an image.  Currently,
   this extension supports four different ways of doing this conversion.  We
   call them conversion "suites" and list for each suite what must be installed
   on your computer: (Only one such suite need be installed.)

   * pdf2svg suite: ``pdf2svg``
   * Netpbm suite: ``pdftoppm`` (part of the Poppler pdf library) and ``pnmtopng``
     (part of the Netpbm package)
   * ImageMagick suite: ``pdftoppm`` (part of the Poppler pdf library) and
     ``convert`` (part of the ImageMagick package)
   * GhostScript suite: ``ghostscript``

Ubuntu Linux
------------

For **Ubuntu Linux** you roughly have to make sure that the following packages
are installed:

A. ``texlive`` and ``texlive-pictures`` (and maybe more LaTeX packages)

B. Depending on the chosen conversion suite the following package(s) have to be
   installed:

   * pdf2svg suite: ``pdf2svg``
   * Netpbm suite: ``poppler-utils`` and ``netpbm``
   * ImageMagick suite: ``poppler-utils`` and ``imagemagick``
   * GhostScript suite: ``ghostscript``

Mac OS X
--------

For **Mac OS X** a possible way of getting this extension working is as follows:

A. Install the `MacTeX <http://tug.org/mactex/>`__ LaTeX distribution which per
   default comes with the ``tikz`` package.

B. To install one of the conversion suites you can install `homebrew
   <https://brew.sh/>`__ and then use homebrew to install the package(s) listed
   under B. as above for Ubuntu Linux.

Windows
-------

For **Windows** do the following:

A. Install the `MiKTeX <http://miktex.org/>`__ LaTeX distribution and include
   the ``tikz`` package when installing.

B. Depending on the chosen conversion suite, you have to install the following:

   * pdf2svg suite:

     Get the Windows binaries from `GitHub
     <https://github.com/jalios/pdf2svg-windows>`__ copy all the files to some
     directory and add this directory to the ``PATH`` environment variable.

   * Netpbm suite:

     - `Xpdf package <http://www.foolabs.com/xpdf/download.html>`__
     - `NetPbm for Windows package
       <http://gnuwin32.sourceforge.net/packages/netpbm.htm>`__

     If you don't want to install the full packages above, you can copy the
     following files to some directory and add this directory to the ``PATH``
     environment variable:

     From Xpdf:

     * ``pdftoppm``

     From NetPbm:

     * ``pnmtopng.exe``
     * ``libnetpbm10.dll``
     * ``libpng13.dll``
     * ``rgb.txt``

     Also, you need to create a new environment variable
     ``RGBDEF=C:\TikzSphinx\rgb.txt`` assuming you copy the files to the
     ``C:\TikzSphinx`` directory.

   * ImageMagick suite:

     Install the `Xpdf package <http://www.foolabs.com/xpdf/download.html>`__
     (same as for the Netpbm suite) and install ImageMagick from `here
     <http://www.imagemagick.org/script/binary-releases.php>`__.

   * GhostScript suite:

     Get the GhostScript binary from `here
     <https://ghostscript.com/download/gsdnld.html>`__, copy it to some
     directory and add this directory to the ``PATH`` environment variable.

.. highlight:: python

.. _configuration:

Configuration
-------------

If you have installed the Ti\ *k*\ z Sphinx extension e.g. using `PyPI
<http://pypi.python.org/pypi/sphinxcontrib-tikz>`__, then you have to load the
extension in the Sphinx project configuration file ``conf.py`` by::

  extensions = ['sphinxcontrib.tikz']

Additionally, the following configuration values are supported:

* Choose the image processing ``‹suite›``, either ``'pdf2svg'``, ``'Netpbm'``,
  ``'ImageMagick'``, ``'GhostScript'`` (``'pdf2svg'`` by default)::

    tikz_proc_suite = ‹suite›

  .. note::

    * If you want your documentation to be built on http://readthedocs.org, you
      have to choose ``GhostScript``.
    * All suites produce png images, excepted ``'pdf2svg'`` which produces svg.

* Choose an image resolution (ignored if ``tikz_proc_suite`` is ``'pdf2svg'``,
  default ``184``)::

    tikz_resolution = ‹number›

* Enable/disable transparent graphics (enabled by default)::

    tikz_transparent = ‹True or False›

* Add ``‹string›`` to the LaTeX preamble used for building the Ti\ *k*\ Z
  picture::

    tikz_latex_preamble = ‹string›

* To support ``\includegraphics{‹file›}`` within a Ti\ *k*\ Z picture, you have to
  configure the directory path(s) where the ``‹file›``\ s reside by setting::

    tikz_includegraphics_path = '‹relative path›'

  or, for multiple directories::

    tikz_includegraphics_path = ['‹relative path 1›', '‹relative path 2›, ...]

  In the above, ``‹relative path›`` is a path relative to the root source directory.
  Within a path, directories must be separated with ``/`` not ``\``.

  .. note:: Internally, this option results in a ``\graphicspath{...}`` LaTeX
     command, of which only one is permitted per LaTeX document.  If you use this
     command in your ``tikz_latex_preamble`` or in ``latex_elements['preamble']``,
     then don't set ``tikz_includegraphics_path``.

* Add ``\usetikzlibrary{‹string›}`` to the LaTeX preamble used for building the
  Ti\ *k*\ Z picture::

    tikz_tikzlibraries = ‹string›

  .. note:: If you want to use the ``latex`` target, then you have to take care to
     include in ``tikz_libraries`` any ``‹tikz libraries›`` given to the ``libs``
     option of the ``tikz`` directive (see :ref:`usage`)

.. note:: If you want to make use of the Ti\ *k*\ Z externalization library for
   the LaTeX build output, then you may want to change the line::

     LATEXOPTS =

   in Sphinx LaTeX Makefile (``/usr/share/sphinx/texinputs/Makefile``) to::

     LATEXOPTS = "-shell-escape"

.. highlight:: rest

.. _usage:

Usage
=====

The extension adds a ``tikz``-directive and a ``tikz``-role.

The **tikz-directive** can be used in two ways::

  .. tikz:: ‹tikz code, potentially broken
     across lines›
     :libs:   ‹tikz libraries›
     :xscale: ‹integer value between 0 and 100›
     :stringsubst:
     :align:  ‹left|center|right›
     :alt:    ‹alternative text›

or::

  .. tikz:: ‹caption, potentially broken
     across lines›
     :libs:   ‹tikz libraries›
     :xscale: ‹integer value between 0 and 100›
     :stringsubst:
     :align:  ‹left|center|right›
     :alt:    ‹alternative text›

     ‹tikz code, potentially broken
     across lines›

The ``‹caption›`` is optional, but if present it is printed as a picture caption
below the picture.

The ``:libs:`` option expects its argument ``‹tikz libraries›`` to be a comma
separated list of Ti\ *k*\ z libraries to use.  If you want to build the LaTeX
target then make sure to add these libraries to the configuration value
``tikz_tikzlibraries`` in ``conf.py``.

The ``:xscale:`` option expects its argument ``‹integer value between 0 and 100›``
a percentage that determines the scaling factor relative to the content width.
For the ``latex`` target, this is ``\columnwidth``, and for the ``html`` target,
the percentage is added to the generated ``<\img>`` as a ``width`` attribute.
The aspect ratio of the image is preserved.

The ``:stringsubst:`` option enables the following string substitution in the
``‹tikz code›``:  Before processing the ``‹tikz code›`` the string ``$wd`` or
``$(wd)`` is replaced by the project root directory.  This is convenient when
referring to some source file in the LaTeX code.

The ``:align:`` option expects ``left``, ``center``, or ``right`` to specify the
horizontal alignment of the image, equivalent to the HTML "text-align" CSS
property.  The default value is ``center``.

The ``:alt:`` option specifies the alternative text, which is a short description
of the image, displayed by applications that cannot display images, or spoken by
applications for visually impaired users. The default value is "Figure made with
TikZ."

The ``‹tikz code›`` is code according to the Ti\ *k*\ Z LaTeX package.  It
behaves as if inside a ``tikzpicture`` environment.  The presence of
``\begin{tikzpicture}`` and ``\end{tikzpicture}``, or any other environment starting
with ``tikz...`` is optional.

Alternatively to providing the ``‹tikz code›``, the ``:include:`` option can be
used to import the code from a file::

  .. tikz::‹caption, potentially broken
     across lines›
     :libs:    ‹tikz libraries›
     :include: ‹filename›
     :xscale:  ‹integer value between 0 and 100›
     :stringsubst:
     :align:   ‹left|center|right›
     :alt:     ‹alternative text›

The **tikz-role** is used as follows::

  :tikz:`‹tikz code›`

The ``‹tikz code›`` is code according to the Ti\ *k*\ z LaTeX package.  It
behaves as if inside a ``\tikz`` macro.

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

  .. tikz:: An Example TikZ Directive with Caption
     :align: left

     \draw[thick,rounded corners=8pt]
     (0,0)--(0,2)--(1,3.25)--(2,2)--(2,0)--(0,2)--(2,2)--(0,0)--(2,0);

.. tikz:: An Example TikZ Directive with Caption
   :align: left

   \draw[thick,rounded corners=8pt]
   (0,0)--(0,2)--(1,3.25)--(2,2)--(2,0)--(0,2)--(2,2)--(0,0)--(2,0);

::

  An example role :tikz:`[thick] \node[blue,draw] (a) {A};
  \node[draw,dotted,right of=a] {B} edge[<-] (a);`


An example role :tikz:`[blue,thick] \node[draw] (a) {A}; \node[draw,dotted,right
of=a] {B} edge[<-] (a);`

Example of a Ti\ *k*\ z picture included from a file:

::

   .. tikz::
      :include: example.tikz
      :align: right

.. tikz::
   :include: example.tikz
   :align: right

Caveats
=======

If you use the ``tikz`` directive inside of a table or a sidebar and you specify
a caption then the LaTeX target built by the sphinx builder will not compile.
This is because, as soon as you specify a caption, the ``tikzpicture``
environment is set inside a ``figure`` environment and hence it is a float and
cannot live inside a table or another float.

If you enable ``:stringsubst:`` and you happen to have any LaTeX math expression
starting with ``wd`` (i.e., you would like to write ``$wd ...`` then you must
insert some white space, e.g., ``$w d ...`` to prevent string substitution.
