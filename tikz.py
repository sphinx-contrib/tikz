# -*- coding: utf-8 -*-

"""
    tikz
    ~~~~

    Render TikZ pictures via dvips and pstoimg

    Author: Christoph Reller
    Email: creller@ee.ethz.ch
    Version: 0.1
    subversion: $Date$ $Revision$
"""    

import tempfile
import posixpath
from os import path, getcwd, chdir, mkdir, system
from subprocess import Popen, PIPE
try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx.errors import SphinxError
from sphinx.util import ensuredir, ENOENT, EPIPE
from sphinx.util.compat import Directive

class TikzExtError(SphinxError):
    category = 'Tikz extension error'

class tikz(nodes.General, nodes.Element):
    pass

class TikzDirective(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {'libs':directives.unchanged}

    def run(self):
        node = tikz()
        node['tikz'] = '\n'.join(self.content)
        node['caption'] = '\n'.join(self.arguments)
        node['libs'] = self.options.get('libs', '')
        return [node]

DOC_HEAD = r'''
\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{amsthm}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{bm}
\usepackage{tikz}
\usetikzlibrary{%s}
\pagestyle{empty}
'''

DOC_BODY = r'''
\begin{document}
\begin{tikzpicture}
%s
\end{tikzpicture}
\end{document}
'''

def render_tikz(self,tikz,libs):
    hashkey = tikz.encode('utf-8')
    fname = 'tikz-%s.png' % (sha(hashkey).hexdigest())
    relfn = posixpath.join(self.builder.imgpath, fname)
    outfn = path.join(self.builder.outdir, '_images', fname)

    if path.isfile(outfn):
        return relfn

    if hasattr(self.builder, '_tikz_warned_latex') or \
       hasattr(self.builder, '_tikz_warned_pvips') or \
       hasattr(self.builder, '_tikz_warned_pstoimg'):
        return None
    
    ensuredir(path.dirname(outfn))

    latex = DOC_HEAD % libs
    latex += self.builder.config.tikz_latex_preamble
    latex += DOC_BODY % tikz
    if isinstance(latex, unicode):
        latex = latex.encode('utf-8')

    if not hasattr(self.builder, '_tikz_tempdir'):
        tempdir = self.builder._tikz_tempdir = tempfile.mkdtemp()
    else:
        tempdir = self.builder._tikz_tempdir

    curdir = getcwd()
    chdir(tempdir)

    tf = open('tikz.tex', 'w')
    tf.write(latex)
    tf.close()
    system('cp tikz.tex /tmp')

    latex_args = ['latex', '--interaction=nonstopmode', 'tikz.tex']

    try:
        try:
            p = Popen(latex_args, stdout=PIPE, stderr=PIPE)
        except OSError, err:
            if err.errno != ENOENT:   # No such file or directory
                raise
            self.builder.warn('LaTeX command cannot be run')
            self.builder._tikz_warned_latex = True
            return None
    finally:
        chdir(curdir)

    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise TikzExtError('latex exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))

    chdir(tempdir)

    dvips_args = ['dvips', 'tikz.dvi']
    try:
        p = Popen(dvips_args, stdout=PIPE, stderr=PIPE)
    except OSError, err:
        if err.errno != ENOENT:   # No such file or directory
            raise
        self.builder.warn('dvips command cannot be run')
        self.builder._tikz_warned_pvips = True
        return None
    finally:
        chdir(curdir)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise TikzExtError('dvips exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))

    chdir(tempdir)

    pstoimg_args = ['pstoimg', '-type', 'png', '-scale', '1.64', \
                    '-antialias', '-aaliastext', '-crop', 'a']
    pstoimg_args += ['-out', outfn, 'tikz.ps']
    try:
        p = Popen(pstoimg_args, stdout=PIPE, stderr=PIPE)
    except OSError, err:
        if err.errno != ENOENT:   # No such file or directory
            raise
        self.builder.warn('pstoimg command cannot be run')
        self.builder._tikz_warned_pstoimg = True
        return
    finally:
        chdir(curdir)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise TikzExtError('pstoimg exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))

    return relfn

def html_visit_tikz(self,node):
    # print "\n***********************************"
    # print "You have entered the following argument"
    # print "***********************************"
    # print node['caption']
    # print "***********************************"
    # print "You have entered the following tikzlibraries"
    # print "***********************************"
    # print node['libs']
    # print "\n***********************************"
    # print "You have entered the following tikz-code"
    # print "***********************************"
    # print node['tikz']
    # print "***********************************"

    libs = self.builder.config.tikz_tikzlibraries + ',' + node['libs']
    libs = libs.replace(' ', '').replace('\t', '').strip(', ')

    try:
        fname = render_tikz(self,node['tikz'],libs)
    except TikzExtError, exc:
        info = str(exc)[str(exc).find('!'):-1]
        sm = nodes.system_message(info, type='WARNING', level=2,
                                  backrefs=[], source=node['tikz'])
        sm.walkabout(self)
        self.builder.warn('display latex %r: ' % node['tikz'] + str(exc))
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
            self.body.append('<p class="caption">%s</p>' % \
                             self.encode(node['caption']).strip())
        self.body.append('</div>')
        raise nodes.SkipNode

def latex_visit_tikz(self, node):
    if node['caption']:
        latex = '\\begin{figure}[htp]\\centering\\begin{tikzpicture}' + \
                node['tikz'] + '\\end{tikzpicture}' + '\\caption{' + \
                self.encode(node['caption']).strip() + '}\\end{figure}'
    else:
        latex = '\\begin{center}\\begin{tikzpicture}' + node['tikz'] + \
            '\\end{tikzpicture}\\end{center}'
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

def setup(app):
    app.add_node(tikz,
                 html=(html_visit_tikz, depart_tikz),
                 latex=(latex_visit_tikz, depart_tikz))
    app.add_directive('tikz', TikzDirective)
    app.add_config_value('tikz_latex_preamble', '', 'html')
    app.add_config_value('tikz_tikzlibraries', '', 'html')
    app.connect('build-finished', cleanup_tempdir)
