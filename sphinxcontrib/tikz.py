# -*- coding: utf-8 -*-

# Copyright (c) 2012-2013 by Christoph Reller. All rights reserved.

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

    Draw pictures with the `TikZ/PGF LaTeX package.

    See README.rst file for details

    Author: Christoph Reller <christoph.reller@gmail.com>
    Version: 0.4.1
"""

import tempfile
import posixpath
import shutil
import sys
import codecs
import os

from os import path, getcwd, chdir, mkdir, system
from string import Template
from subprocess import Popen, PIPE, call
try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha

from docutils import nodes, utils
from docutils.parsers.rst import directives

from sphinx.errors import SphinxError
try:
    from sphinx.util.osutil import ensuredir, ENOENT, EPIPE
except:
    from sphinx.util import ensuredir, ENOENT, EPIPE

from sphinx.util.compat import Directive

_Win_ = sys.platform[0:3] == 'win'

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
    option_spec = {'libs':directives.unchanged,'stringsubst':directives.flag, 'include':directives.unchanged}

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
\documentclass[12pt,preview,tikz]{standalone}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{tikz}
\usepackage{pgfplots}
\usetikzlibrary{%s}
\pagestyle{empty}
'''

DOC_BODY = r'''
\begin{document}
%s
\end{document}
'''

def render_tikz(self,node,libs='',stringsubst=False):
    tikz = node['tikz']
    hashkey = tikz.encode('utf-8')
    fname = 'tikz-%s.png' % (sha(hashkey).hexdigest())
    relfn = posixpath.join(self.builder.imgpath, fname)
    outfn = path.join(self.builder.outdir, '_images', fname)

    if path.isfile(outfn):
        return relfn

    if hasattr(self.builder, '_tikz_warned'):
        return None

    ensuredir(path.dirname(outfn))
    curdir = getcwd()

    latex = DOC_HEAD % libs
    latex += self.builder.config.tikz_latex_preamble
    if stringsubst:
        tikz = Template(tikz).substitute(wd=curdir.replace('\\','/'))
    if 'include' not in node:
        tikz = '\\begin{tikzpicture}\n' + tikz + '\n\\end{tikzpicture}'
    latex += DOC_BODY % tikz
    if isinstance(latex, unicode):
        latex = latex.encode('utf-8')

    chdir(app.builder._tikz_tempdir)

    tf = open('tikz.tex', 'wb')
    tf.write(latex)
    tf.close()

    try:
        try:
            p = Popen(['pdflatex', '--interaction=nonstopmode', 'tikz.tex'],
                      stdout=PIPE, stderr=PIPE)
        except OSError as err:
            if err.errno != ENOENT:   # No such file or directory
                raise
            self.builder.warn('LaTeX command cannot be run')
            self.builder._tikz_warned = True
            return None
    finally:
        chdir(curdir)

    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise TikzExtError('Error (tikz extension): latex exited with error:\n'
                           '[stderr]\n%s\n[stdout]\n%s' % (stderr, stdout))

    chdir(app.builder._tikz_tempdir)

    # the following does not work for pdf patterns
    # p1 = Popen(['convert', '-density', '120', '-colorspace', 'rgb',
    #             '-trim', 'tikz.pdf', outfn], stdout=PIPE, stderr=PIPE)
    # stdout, stderr = p1.communicate()

    if self.builder.config.tikz_transparent:
        device = "pngalpha"
    else:
        device = "png256"

    try:
        p = Popen(['ghostscript', '-dBATCH', '-dNOPAUSE', '-sDEVICE=%s' % device, '-sOutputFile=%s' % outfn, '-r100x100', '-f', 'tikz.pdf',],
              stdout=PIPE, stderr=PIPE, stdin=PIPE)
    except OSError as e:
        if e.errno != ENOENT:   # No such file or directory
            raise
        self.builder.warn('ghostscript command cannot be run')
        self.builder.warn(err)
        self.builder._tikz_warned = True
        chdir(curdir)
        return None
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        self.builder._tikz_warned = True
        raise TikzExtError('Error (tikz extension): ghostscript exited with error:'
                           '\n[stderr]\n%s\n[stdout]\n%s' % (stderr, stdout))

    chdir(curdir)
    return relfn

def html_visit_tikzinline(self,node):
    libs = self.builder.config.tikz_tikzlibraries
    libs = libs.replace(' ', '').replace('\t', '').strip(', ')
    try:
        fname = render_tikz(self,node,libs);
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

def html_visit_tikz(self,node):
    libs = self.builder.config.tikz_tikzlibraries + ',' + node['libs']
    libs = libs.replace(' ', '').replace('\t', '').strip(', ')

    try:
        fname = render_tikz(self,node,libs,node['stringsubst'])
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
        cnt,pos = 1,1
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
    if 'include' in node:
        begTikzPic = ''
        endTikzPic = ''
        node['tikz']=node['tikz'].replace('\r\n','\n')
    else:
        begTikzPic = '\\begin{tikzpicture}'
        endTikzPic = '\\end{tikzpicture}'

    if node['caption']:
        if node['stringsubst']:
            node['tikz'] = node['tikz'] % {'wd': getcwd()}
        latex = '\\begin{figure}[htp]\\centering' + begTikzPic + \
                node['tikz'] + endTikzPic + '\\caption{' + \
                self.encode(node['caption']).strip() + '}\\end{figure}'
    else:
        latex = '\\begin{center}' + begTikzPic + node['tikz'] + \
            endTikzPic + '\\end{center}'
    self.body.append(latex)

def depart_tikz(self,node):
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
        sty_path = os.path.join(app.builder._tikz_tempdir, "sphinxcontribtikz.sty")
        sty = open(sty_path, mode="w")
        sty.write(r"\RequirePackage{tikz}" + "\n")
        sty.write(r"\RequirePackage{amsmath}" + "\n")
        sty.write(r"\RequirePackage{amsfonts}" + "\n")
        sty.write(r"\RequirePackage{pgfplots}" + "\n")
        sty.write(app.builder.config.tikz_latex_preamble + "\n")
        sty.write(r"\usetikzlibrary{%s}" % app.builder.config.tikz_tikzlibraries.replace(' ', '').replace('\t', '').strip(', ') + "\n")
        sty.close()

        app.builder.config.latex_additional_files.append(sty_path)
        app.add_latex_package("sphinxcontribtikz")

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
    app.connect('build-finished', cleanup_tempdir)
    app.connect('builder-inited', builder_inited)
