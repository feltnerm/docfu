#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
docfu
-----

Generates per-branch and/or -version documentation from Markdown files via a git
repository.

To use:
    from docfu import Docfu

    df = Docfu(source="~/Projects/foo/docs", dest="~/public_html/foo/")

Then you have access to the Docfu api which will allow you to:
    * `df.render()` -- render docs by running them through a Markdown processor 
    then finally a Jinaj2 processor. Returns an string of HTML ready to be
    written to file or returned as a response on a server.

:copyright: (c) 2013 by Mark Feltner
:license: MIT see LICENSE for more details
"""

import os, os.path, random, shlex, shutil, subprocess, sys, tempfile, urlparse

import jinja2
import jinja2.ext
from pprint import pprint

import markdown2 as md 

from webassets import Environment as AssetsEnvironment
from webassets import Bundle
from webassets.ext.jinja2 import AssetsExtension

import logging

logging.basicConfig()
logger = logging.getLogger('docfu')
logger.setLevel(logging.DEBUG)

#
# Utils
#

def uri_parse(u):
    """ A provided url can be one of:
        * github repo: "feltnerm/foo"
        * git path: "http://github.com/feltnerm/foo.git"
        * filesystem path: "~/Projects/foo"

        This functions parses a provided URL string matching one of those 
        three categories. """
    url = urlparse.urlparse(u)

    if not url.scheme:
        if u.count('/') == 1 and len(u.split('/')) == 2:
            # github url
            u = u.strip()
            u = "http://github.com/" + u
            url = urlparse.urlparse(u)
        else:
            u = "file://" + os.path.expanduser(u)
            url = urlparse.urlparse(u)

    return urlparse.urlunparse(url)


#
# Git / repository utils
#
def git_clone(git_url):
    """ Clone a github url into a temp directory. Set a global object to 
    this class so it can be closed. """

    path = tmp_mk()
    git_clone_cmd = shlex.split('git clone %s %s' % (str(git_url), str(path)))
    retcode = subprocess.check_call(git_clone_cmd)
    logger.debug("Cloned repository. \n %s" % git_clone_cmd)
    return path 


def git_checkout(git_repo_path, branch=None, tag=None):
    """ Checkout the code at git_repo_path. Ref is the specific branch or 
    tag to use. """
    if branch:
        git_checkout_cmd = shlex.split('git checkout %s' % str(branch))

    if tag:
        git_checkout_cmd = shlex.split('git checkout -b %s' % str(tag))

    stdout, stderr = subprocess.Popen(git_checkout_cmd, cwd="%s" % str(git_repo_path)).communicate()
    logger.debug("Checked out source repository. \n %s" % git_checkout_cmd)

#
# Temporary File / Directory Utilities
#

def tmp_mk():
    """ Make a temporary directory, already prefixed with `docfu-`, 
    in `/tmp/`."""
    path = tempfile.mkdtemp(prefix='docfu-', dir='/tmp')
    logger.debug("Temporary path created at: %s" % path)
    return path


def tmp_close(path):
    """ Remove the directory denoted by `path`. """
    try:
        shutil.rmtree(path)
        logger.debug("Temporary path removed at: %s" % path)
    except Exception, e:
        if e.errno != 2:
            logger.error("Cannot remove temporary path %s. Error %s" % (path, e))
            raise

def tmp_cp(src):
    """ Copy the source directory to a tmp directory. 

    @TODO: ignore version control and other things.
    """
    dest = tmp_mk()
    dest = os.path.join('/tmp', 'docfu-%s' % random.randint(999, 10000))
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns('*.git', 'node_modules'))
    logger.debug("Copied source files %s to tempdir %s" % (src, dest))
    return dest

class MarkdownJinja(jinja2.ext.Extension):
    """ Add markdown support to Jinja2 templates. 

    Usage:

        {% markdown %}
        Hello world
        ===========

        1. One
        2. Two
        3. Three

            public void main(String[] args) {
                // ...
            }
        {% endmarkdown %}
    """

    tags = set(['markdown'])

    def __init__(self, environment):
        super(MarkdownJinja, self).__init__(environment)
        environment.extend(
            markdowner=md.Markdown(
                extras=['wiki-tables', 'cuddled-lists', 'fenced-code-blocks', 
                    'header-ids', 'smarty-pants',])
        )   

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(
            ['name:endmarkdown'],
            drop_needle=True
        )
        return jinja2.nodes.CallBlock(
            self.call_method('_markdown_support'),
            [],
            [],
            body
        ).set_lineno(lineno)

    def _markdown_support(self, caller):
        return self.environment.markdowner.convert(caller()).strip()


class Docfu(object):
    """
    A class which converts Markdown files in one git directory to HTML files in
    another. Made for documentation generation, this class also provides global 
    template variables and processing."""

    def __init__(self, uri, dest, **kwargs):
        self.uri = uri_parse(uri)
        self.dest = os.path.abspath(dest)
        self.source_dir = kwargs.get('source_dir')
        self.templates_dir = kwargs.get('templates_dir')
        self.assets_dir = kwargs.get('assets_dir')
        self.template_globals = kwargs['template_globals'] if 'template_globals' in kwargs else {}

        if self.uri.startswith('file://'):
            self.uri = self.uri.replace("file://", "")
            self.repository_dir = tmp_cp(self.uri)
            self.git_repo = False
        else:
            self.repository_dir = git_clone(self.uri)
            self.git_repo = True 

        self.source = os.path.join(self.repository_dir, self.source_dir)
        logger.info("> Source: %s" % self.source)

        self.branch = kwargs['branch'] if 'branch' in kwargs else None
        self.tag = kwargs['tag'] if 'tag' in kwargs else None
        if self.branch and self.git_repo:
            git_checkout(self.repository_dir, branch=self.branch)
        elif self.tag and self.git_repo:
            git_checkout(self.repository_dir, tag=self.tag)

        self.template_globals['BRANCH'] = self.branch
        self.template_globals['TAG'] = self.tag

        path = self.dest
        d = self.dest
        if self.branch:
            path = os.path.join(self.dest, 'branches', 
                self.branch.replace("/", "_"))

        if self.tag:
            path = os.path.join(self.dest, 'tags', self.tag)

        self.dest = path
        self.template_globals['ASSETS'] = os.path.join(self.dest, 'assets').replace(d, "")

        if os.path.exists(self.dest):
            shutil.rmtree(self.dest)
        os.makedirs(self.dest)

        if os.path.exists(os.path.join(self.dest, 'assets')):
            shutil.rmtree(os.path.join(self.dest, 'assets'))
        shutil.copytree(
                os.path.join(self.repository_dir, self.assets_dir),
                os.path.join(self.dest, 'assets'))

        #self._assets_env = AssetsEnvironment(
        #        load_path=os.path.join(self.repository_dir, self.assets_dir), 
        #        directory=os.path.join(self.dest, 'assets'),
        #        url='assets'
        #)

        self._env = jinja2.Environment(
                extensions=[MarkdownJinja],
                loader=jinja2.FileSystemLoader(
                    os.path.join(self.repository_dir, self.templates_dir)
                )
        )

        self.source_files = set()

        for current, dirs, files in os.walk(os.path.join(self.repository_dir, self.source_dir)):
            for f in files:
                self.source_files.add(os.path.join(current, f))

        #self._setup_bundles()

    def _setup_bundles(self):
        pass
        #self._assets_env.register('js_all', 'js/vendor/jquery-1.9.1.min.js', 'js/vendor/bootstrap.min.js', 'js/main.js')
        #self._assets_env.register('css_all', 'css/bootstrap.min.css', 'css/bootstrap-responsive.min.css', 'css/main.css')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        logger.info("> Cleaning up ...")
        #tmp_close(self.repository_dir)

    def __call__(self):
        self.render()

    def render(self):
        """ Render the docs found in the repository's source-dir into the 
        destination dir. """
        logger.info("\n### Rendering documents ###\n")
        for source_path in self.source_files:
            source_file = open(source_path, 'r')
            source_data = source_file.read().decode('utf-8', 'replace') 
            source_dest = source_path.replace(os.path.join(self.repository_dir, self.source_dir), "")
            source_dest = os.path.join(self.dest, "html") + source_dest
            source_name = os.path.basename(source_dest)
            self._render(source_name, source_data, source_dest)
            source_file.close()

        logger.info("\n### Documents rendered ###\n\n")
        logger.debug("%s" % self.dest)

    def _render(self, name, data, dest): 
        """ Render a single file. """
        logger.info("\t> Rendering document: %s" % name)
        logger.debug("\t\t %s @ %s " % (name, dest))

        base_template = "base.html"
        template = self._env.get_template(base_template)
        html = template.render(content=data, **self.template_globals)
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        # make extension .html
        dest = os.path.splitext(dest)[0] + '.html'
        with open(dest, 'wb') as output:
            output.write(html.encode('utf-8'))
        logger.info("\t Rendered: %s" % dest)
