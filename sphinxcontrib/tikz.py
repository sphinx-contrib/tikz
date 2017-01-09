# -*- coding: utf-8 -*-

# Copyright (c) 2012-2015 by Christoph Reller. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.

#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY CHRISTOPH RELLER ''AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL CHRISTOPH RELLER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Christoph Reller.

"""
    sphinxcontrib.tikz
    ~~~~~~~~~~~~~~~~~~

    Draw pictures with the TikZ/PGF LaTeX package.

    See README.rst file for details

    Author: Christoph Reller <christoph.reller@gmail.com>
    Version: 0.4.3
"""

import contextlib
import tempfile
import posixpath
import shutil
import sys
import codecs
import os
import re

from os import path, getcwd, chdir
from string import Template
from subprocess import Popen, PIPE
try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha

from docutils import nodes, utils
from docutils.parsers.rst import directives

from sphinx.errors import SphinxError
try:
    from sphinx.util.osutil import ensuredir, ENOENT
except:
    from sphinx.util import ensuredir, ENOENT

from sphinx.util.compat import Directive

_Win_ = sys.platform[0:3] == 'win'

# TODO: Check existence of executables with subprocess.check_call


@contextlib.contextmanager
def changedir(directory):
    """Context to temporary change directory"""
    curdir = getcwd()
    chdir(directory)
    try:
        yield
    finally:
        chdir(curdir)


def system(command, builder, outfile=None):
    """Perform a system call, handling errors.

    :param list command: System command to run.
    :param builder: Sphinx builder object performing the call.
    :param str outfile: Output file in which to store command output.
    """
    binary = command[0]
    try:
        process = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    except OSError as err:
        if err.errno != ENOENT:   # No such file or directory
            raise
        builder.warn('%s command cannot be run' % binary)
        builder.warn(err)
        builder._tikz_warned = True
        return None
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        builder._tikz_warned = True
        raise TikzExtError('Error (tikz extension): %s exited with error:'
                           '\n[stderr]\n%s\n[stdout]\n%s'
                           % (binary, stderr, stdout))
    if outfile is not None:
        f = open(outfile, 'wb')
        f.write(stdout)
        f.close()


class TikzExtError(SphinxError):
    category = 'Tikz extension error'


class tikzinline(nodes.Inline, nodes.Element):
    pass


def tikz_role(role, rawtext, text, lineno, inliner, option={}, content=[]):
    tikz = utils.unescape(text, restore_backslashes=True)
    return [tikzinline(tikz=tikz)], []


class tikz(nodes.Part, nodes.Element):
    pass


class TikzDirective(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {'libs': directives.unchanged,
                   'stringsubst': directives.flag,
                   'include': directives.unchanged}

    def run(self):
        node = tikz()

        if 'include' in self.options:
            node['include'] = self.options['include']
            env = self.state.document.settings.env
            rel_filename, filename = env.relfn2path(node['include'])
            env.note_dependency(rel_filename)
            try:
                fp = codecs.open(filename, 'r', 'utf-8')
                try:
                    node['tikz'] = '\n' + fp.read() + '\n'
                finally:
                    fp.close()
            except (IOError, OSError):
                return [self.state.document.reporter.warning(
                    'External Tikz file %r not found or reading '
                    'it failed' % filename, line=self.lineno)]
            node['caption'] = ''
            if self.arguments:
                node['caption'] = '\n'.join(self.arguments)
        else:
            if not self.content:
                node['caption'] = ''
                node['tikz'] = '\n'.join(self.arguments)
            else:
                node['tikz'] = '\n'.join(self.content)
                node['caption'] = '\n'.join(self.arguments)
        
        node['libs'] = self.options.get('libs', '')
        if 'stringsubst' in self.options:
            node['stringsubst'] = True
        else:
            node['stringsubst'] = False
        if node['tikz'] == '':
            return [self.state_machine.reporter.warning(
                    'Ignoring "tikz" directive without content.',
                    line=self.lineno)]
        return [node]

DOC_HEAD = r'''
\documentclass[12pt,tikz]{standalone}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{pgfplots}
\usetikzlibrary{%s}
\pagestyle{empty}
'''

DOC_BODY = r'''
\begin{document}
%s
\end{document}
'''

OUT_EXTENSION = {
    'GhostScript': 'png',
    'ImageMagick': 'png',
    'Netpbm': 'png',
    'pdf2svg': 'svg',
    }


def cleanup_tikzcode(self, node):
    tikz = node['tikz']
    tikz = tikz.replace('\r\n', '\n')
    tikz = re.sub('^\s*%.*$\n', '', tikz, 0, re.MULTILINE)
    tikz = re.sub('^\s*$\n', '', tikz, 0, re.MULTILINE)
    if not tikz.startswith('\\begin{tikzpicture}'):
        tikz = '\\begin{tikzpicture}\n' + tikz + '\n\\end{tikzpicture}'
    if 'stringsubst' in node:
        tikz = Template(tikz).safe_substitute(wd=getcwd().replace('\\', '/'))
    return tikz


def render_tikz(self, node, libs='', stringsubst=False):
    tikz = cleanup_tikzcode(self, node)
    hashkey = tikz.encode('utf-8')
    fname = 'tikz-%s.%s' % (sha(hashkey).hexdigest(),
                            OUT_EXTENSION[self.builder.config.tikz_proc_suite])
    relfn = posixpath.join(self.builder.imgpath, fname)
    outfn = path.join(self.builder.outdir, '_images', fname)

    if path.isfile(outfn):
        return relfn

    if hasattr(self.builder, '_tikz_warned'):
        return None

    ensuredir(path.dirname(outfn))

    latex = DOC_HEAD % libs
    latex += self.builder.config.tikz_latex_preamble
    latex += DOC_BODY % tikz
    latex = latex.encode('utf-8')

    with changedir(self.builder._tikz_tempdir):

        tf = open('tikz.tex', 'wb')
        tf.write(latex)
        tf.close()

        system(['pdflatex', '--interaction=nonstopmode', 'tikz.tex'],
               self.builder)

        if self.builder.config.tikz_proc_suite in ['ImageMagick', 'Netpbm']:

            system(['pdftoppm', '-r', '400', '-singlefile', 'tikz.pdf',
                    'tikz'], self.builder)

            if self.builder.config.tikz_proc_suite == "ImageMagick":
                if self.builder.config.tikz_transparent:
                    convert_args = ['-fuzz', '2%', '-transparent', 'white']
                else:
                    convert_args = []
                system(['convert', '-trim'] + convert_args +
                       ['tikz.ppm', outfn], self.builder)

            elif self.builder.config.tikz_proc_suite == "Netpbm":
                if self.builder.config.tikz_transparent:
                    pnm_args = ['-transparent', 'rgb:ff/ff/ff']
                else:
                    pnm_args = []
                system(['pnmtopng'] + pnm_args + ["tikz.ppm"], self.builder,
                       outfile=outfn)

        elif self.builder.config.tikz_proc_suite == "GhostScript":
            if self.builder.config.tikz_transparent:
                device = "pngalpha"
            else:
                device = "png256"
            system(['ghostscript', '-dBATCH', '-dNOPAUSE',
                    '-sDEVICE=%s' % device, '-sOutputFile=%s' % outfn,
                    '-r120x120', '-f', 'tikz.pdf'], self.builder)
        elif self.builder.config.tikz_proc_suite == "pdf2svg":
            system(['pdf2svg', 'tikz.pdf', outfn], self.builder)
        else:
            self.builder._tikz_warned = True
            raise TikzExtError('Error (tikz extension): Invalid configuration '
                               'value for tikz_proc_suite')

        return relfn


def html_visit_tikzinline(self, node):
    libs = self.builder.config.tikz_tikzlibraries
    libs = libs.replace(' ', '').replace('\t', '').strip(', ')
    try:
        fname = render_tikz(self, node, libs)
    except TikzExtError as exc:
        info = str(exc)[str(exc).find('!'):-1]
        sm = nodes.system_message(info, type='WARNING', level=2,
                                  backrefs=[], source=node['tikz'])
        sm.walkabout(self)
        self.builder.warn('display latex %r: \n' % node['tikz'] + str(exc))
        raise nodes.SkipNode
    if fname is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="math">%s</span>' %
                         self.encode(node['tikz']).strip())
    else:
        self.body.append('<img class="math" src="%s" alt="%s"/>' %
                         (fname, self.encode(node['tikz']).strip()))
        raise nodes.SkipNode


def html_visit_tikz(self, node):
    libs = self.builder.config.tikz_tikzlibraries + ',' + node['libs']
    libs = libs.replace(' ', '').replace('\t', '').strip(', ')
    try:
        fname = render_tikz(self, node, libs, node['stringsubst'])
    except TikzExtError as exc:
        info = str(exc)[str(exc).find('!'):-1]
        sm = nodes.system_message(info, type='WARNING', level=2,
                                  backrefs=[], source=node['tikz'])
        sm.walkabout(self)
        self.builder.warn('display latex %r: \n' % node['tikz'] + str(exc))
        raise nodes.SkipNode
    if fname is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="math">%s</span>' %
                         self.encode(node['tikz']).strip())
    else:
        self.body.append(self.starttag(node, 'div', CLASS='figure'))
        self.body.append('<p>')
        self.body.append('<img src="%s" alt="%s" /></p>\n' %
                         (fname, self.encode(node['tikz']).strip()))
        if node['caption']:
            self.body.append('<p class="caption">%s</p>' %
                             self.encode(node['caption']).strip())
        self.body.append('</div>')
        raise nodes.SkipNode


def latex_visit_tikzinline(self, node):
    tikz = node['tikz']
    if tikz[0] == '[':
        cnt, pos = 1, 1
        while cnt > 0 and cnt < len(tikz):
            if tikz[pos] == '[':
                cnt = cnt + 1
            if tikz[pos] == ']':
                cnt = cnt - 1
            pos = pos + 1
        tikz = tikz[:pos] + '{' + tikz[pos:]
    else:
        tikz = '{' + tikz
    self.body.append('\\tikz' + tikz + '}')
    raise nodes.SkipNode


def latex_visit_tikz(self, node):
    tikz = cleanup_tikzcode(self, node)
    if node['caption']:
        latex = '\\begin{figure}[htp]\\centering' + tikz \
                + '\\caption{' + self.encode(node['caption']).strip() \
                + '}\\end{figure}'
    else:
        latex = '\\begin{center}' + tikz + '\\end{center}'
    self.body.append(latex)


def depart_tikz(self, node):
    pass


def cleanup_tempdir(app, exc):
    if exc:
        return
    if not hasattr(app.builder, '_tikz_tempdir'):
        return
    try:
        shutil.rmtree(app.builder._tikz_tempdir)
    except Exception:
        pass


def builder_inited(app):
    app.builder._tikz_tempdir = tempfile.mkdtemp()

    if app.builder.name == "latex":
        sty_path = os.path.join(app.builder._tikz_tempdir,
                                "sphinxcontribtikz.sty")
        sty = open(sty_path, mode="w")
        sty.write(r"\RequirePackage{tikz}" + "\n")
        sty.write(r"\RequirePackage{amsmath}" + "\n")
        sty.write(r"\RequirePackage{amsfonts}" + "\n")
        sty.write(r"\RequirePackage{pgfplots}" + "\n")
        sty.write(app.builder.config.tikz_latex_preamble + "\n")
        tikzlibs = app.builder.config.tikz_tikzlibraries
        tikzlibs = tikzlibs.replace(' ', '')
        tikzlibs = tikzlibs.replace('\t', '')
        tikzlibs = tikzlibs.strip(', ') + "\n"
        sty.write(r"\usetikzlibrary{%s}" % tikzlibs)
        sty.close()

        app.builder.config.latex_additional_files.append(sty_path)


def which(program):
    if sys.platform == "win32" and not program.endswith(".exe"):
        program += ".exe"

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for p in os.environ["PATH"].split(os.pathsep):
            p = p.strip('"')
            exe_file = os.path.join(p, program)
            if is_exe(exe_file):
                return exe_file

    return None


def setup(app):
    app.add_node(tikz,
                 html=(html_visit_tikz, depart_tikz),
                 latex=(latex_visit_tikz, depart_tikz))
    app.add_node(tikzinline,
                 html=(html_visit_tikzinline, depart_tikz),
                 latex=(latex_visit_tikzinline, depart_tikz))
    app.add_role('tikz', tikz_role)
    app.add_directive('tikz', TikzDirective)
    app.add_config_value('tikz_latex_preamble', '', 'html')
    app.add_config_value('tikz_tikzlibraries', '', 'html')
    app.add_config_value('tikz_transparent', True, 'html')

    # fallback to another value depending what is on the system
    suite = 'pdf2svg'
    if not which('pdf2svg'):
        suite = 'GhostScript'
        if not which('ghostscript'):
            suite = 'ImageMagick'
            if not which('pnmcrop'):
                suite = 'Netpbm'
    app.add_config_value('tikz_proc_suite', suite, 'html')

    app.connect('build-finished', cleanup_tempdir)
    app.connect('builder-inited', builder_inited)
