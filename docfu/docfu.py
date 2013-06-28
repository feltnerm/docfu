#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
docfu
-----

Generates per-branch and/or -version documentation from Markdown files via a git
repository.

To use:
    from docfu import Docfu

    with Docfu(uri="feltnerm/Docfu", root="docs/", dest="/tmp/docs") as df:
        df()

Then you have access to the Docfu api which will allow you to:
    * `df.render()` -- render docs by running them through a Markdown processor 
    then finally a Jinaj2 processor. Returns an string of HTML ready to be
    written to file or returned as a response on a server.

:copyright: (c) 2013 by Mark Feltner
:license: MIT see LICENSE for more details
"""

import logging, os.path, shutil

import jinja2

from ext import MarkdownJinja
from util import (git_clone, git_checkout, tmp_mk, tmp_close, tmp_cp, 
        walk_files, uri_parse)

logger = logging.getLogger('docfu')

class Docfu(object):
    """
    A class which converts Markdown files in one git directory to HTML files in
    another. Made for documentation generation, this class also provides global 
    template variables and processing."""

    def __init__(self, uri, root, dest, **kwargs):
        self.uri = uri_parse(uri)
        self.root = root
        dest = os.path.abspath(os.path.expanduser(dest))

        self.template_globals = kwargs['template_globals'] if 'template_globals' in kwargs else {}
        self.base_template = kwargs['base_template'] if 'base_template' in kwargs else 'base.html'

        if self.uri.startswith('file://'):
            self.uri = self.uri.replace("file://", "")
            self.repository_dir = tmp_cp(self.uri)
            self.git_repo = False
        else:
            self.repository_dir = git_clone(self.uri)
            self.git_repo = True 

        source_src_dir = kwargs['source_dir'] if 'source_dir' in kwargs else join(self.root, 'src')
        source_src_dir = kwargs['source_dir'] if 'source_dir' in kwargs else os.path.join(self.root, 'src')
        assets_src_dir = kwargs['assets_dir'] if 'assets_dir' in kwargs else os.path.join(self.root, 'assets')
        templates_src_dir = kwargs['templates_dir'] if 'templates_dir' in kwargs else os.path.join(self.root, 'templates')
        self.source_src_dir = os.path.join(self.repository_dir, source_src_dir)
        self.assets_src_dir = os.path.join(self.repository_dir, assets_src_dir)
        self.templates_src_dir = os.path.join(self.repository_dir, templates_src_dir)
        branch = kwargs['branch'] if 'branch' in kwargs else None
        tag = kwargs['tag'] if 'tag' in kwargs else None

        if branch and self.git_repo:
            self.git_ref_type = 'branch'
            self.git_ref_val = branch

        elif tag and self.git_repo:
            self.git_ref_type = 'tag'
            self.git_ref_val = tag
            git_checkout(self.repository_dir, tag=self.tag)

        git_checkout(self.repository_dir, self.git_ref_type, self.git_ref_val)

        if "/" in self.git_ref_val:
            self.git_ref_val = self.git_ref_val.replace("/", "_")

        self.dest = os.path.join(dest, self.git_ref_type, self.git_ref_val)
        self.source_dest_dir = os.path.join(self.dest, 'html')
        self.assets_dest_dir = os.path.join(self.dest, 'assets')
        self._init_directories()

        self.template_globals = self._init_template_globals()

        logger.debug(
        """> Docfu
    uri: %s
    root: %s
    dest: %s

    >> Source
    source: %s
    assets: %s
    templates: %s

    >> Dest
    dest: %s
    assets: %s

    >> Git ref
    type: %s
    value: %s
        """ % (self.uri, self.root, self.dest, 
            self.source_src_dir, self.assets_src_dir, self.templates_src_dir, 
            self.source_dest_dir, self.assets_dest_dir,
            self.template_globals['GIT_REF_TYPE'], 
            self.template_globals['GIT_REF']))

        logger.debug(self.template_globals)

        self.source_files = walk_files(self.source_src_dir)
        self._env = self._init_template_engine()


    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        logger.info("Cleaning up ...")
        tmp_close(self.repository_dir)

    def __call__(self):
        self.render()

    def _init_directories(self):
        """ Initialize the directories to compile documentation in.
        First, wipe any pre-existing documentation for the same
        release. Then, create directories, and copy over assets.
        """
        if os.path.exists(self.dest):
            logger.debug("`shutil.rmtree(%s)`" % self.dest)
            shutil.rmtree(self.dest)

        logger.debug("`os.makedirs(%s)`" % self.dest)
        os.makedirs(self.dest)
        logger.debug("`os.makedirs(%s)`" % self.source_dest_dir)
        os.makedirs(self.source_dest_dir)

        logger.debug("`shutil.copytree.(%s, %s)`" % (self.assets_src_dir, self.assets_dest_dir))
        shutil.copytree(self.assets_src_dir, self.assets_dest_dir)

    def _init_template_globals(self):
        """ Return a dictionary of template globals to use in the
        templates. """
        return {
                'GIT_REF_TYPE': self.git_ref_type,
                'GIT_REF': self.git_ref_val,
                'ASSETS': self.assets_dest_dir
                }

    def _init_template_engine(self, **options):
        """ Return a jinja2 Environment. """
        defaults = {
                'extensions': [MarkdownJinja],
                'loader': jinja2.FileSystemLoader(self.templates_src_dir)
        }

        defaults.update(options)
        return jinja2.Environment(**defaults)

    def render(self):
        """ Render the docs found in the repository's source-dir into the 
        destination dir. """
        logger.info("Rendering documents @ %s \
            \n##################################################" % self.dest)

        for source_path in self.source_files:
            with open(source_path, 'r') as source_file:
                source_data = source_file.read().decode('utf-8', 'replace') 
                source_dest = self.source_dest_dir + source_path.replace(self.source_src_dir, "")
                source_name = os.path.basename(source_dest)
                self._render(source_name, source_data, source_dest)

        logger.info("Documents rendered @ %s \
            \n##################################################" % self.dest)

    def _render(self, name, content, dest): 
        """ Render a single file. """
        logger.info("\t> Rendering document: %s --> %s" % (name, dest))
        template = self._env.get_template(self.base_template)
        html = template.render(content=content, **self.template_globals)
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        # make extension .html
        dest = os.path.splitext(dest)[0] + '.html'
        with open(dest, 'wb') as output:
            output.write(html.encode('utf-8'))
