==============================================
 Description of the ``tikz`` Sphinx extension
==============================================

Enable the use of the TikZ LaTeX package to draw nice pictures.

Prerequisites
=============

You need ``latex``, the ``tikz`` and the ``amsmath`` packages, ``dvips`` and
``pstoimg``.  We don't use ``dvipng`` as the math Sphinx extensions do because
there is an issue with cropping the image if postscript specials are used.

The ``tikz`` Sphinx extension consists of the single file ``tikz.py``.

In the Sphinx project configuration file ``conf.py`` you need to:

- add the directory where ``tikz.py`` is located to ``sys.path``, e.g. by::

    sys.path.append('‹absolute path to directory›')

- load the extension by::

    extensions = ['tikz']

If you want to produce latex code then you should add the ``tikz`` package and
all ``tikzlibraries`` to the latex preamble in ``conf.py``, e.g::

  latex_preamble = '''
  \usepackage{tikz}
  \usetikzlibrary{arrows,fit}
  '''

Usage
=====

The extension adds a ``tikz``-directive which look as follows::

  .. tikz:: ‹caption potentially broken
     across lines›
     :libs: ‹tikz libraries›

     ‹tikz code›

The caption is optional, but if present is printed as a picture caption centered
below the picture.

The ``‹tikz libraries›`` option is a comma separated list of tikz libraries to
use.  If you want to build latex code then make sure that you add these to
``latex_preamble`` in ``conf.py``.

The ``‹tikz code›`` finally is code according to the tikz latex package.

----

Christoph Reller
