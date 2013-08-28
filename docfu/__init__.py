# -*- coding: utf-8 -*-
from __future__ import with_statement

import logging
import os.path
import shutil
import sys
import time

import jinja2
import markdown

from ext import render_markdown, MarkdownJinja
from util import (
    git_clone, git_checkout,
    list_doc_tree, list_refs,
    tmp_mk, tmp_close, tmp_cp,
    get_git_tag, get_git_branch,
    parse_package_json, walk_files, uri_parse
)

__major__ = 0
__minor__ = 1
__micro__ = 0
__version__ = "{0}.{1}.{2}".format(__major__, __minor__, __micro__)

logger = logging.getLogger(__name__)


class Docfu(object):
    """
    A class which converts Markdown files in one git directory to HTML files in
    another. Made for documentation generation, this class also provides global
    template variables and processing."""

    def __init__(self, uri, root, dest, **kwargs):
        """ Docfu initialzation. """
        self.uri = uri_parse(uri)
        self.root = os.path.normpath(root)
        dest = os.path.abspath(os.path.expanduser(dest))

        self.template_globals = {}
        if 'template_globals' in kwargs:
            self.template_globals = kwargs['template_globals']

        self.base_template = 'base.html'
        if 'base_template' in kwargs:
            self.base_template = kwargs['base_template']

        if self.uri.startswith('file://'):
            self.uri = self.uri.replace("file://", "")
            self.repository_dir = tmp_cp(os.path.expanduser(self.uri))
            self.git_repo = False
        else:
            self.repository_dir = git_clone(self.uri)
            self.git_repo = True

        source_src_dir = self.root
        if 'source_dir' in kwargs:
            source_src_dir = kwargs['source_dir']

        assets_src_dir = os.path.join(self.root, '_static')
        if 'assets_dir' in kwargs:
            assets_src_dir = kwargs['assets_dir']

        templates_src_dir = os.path.join(self.root, '_templates')
        if 'templates_dir' in kwargs:
            templates_src_dir = kwargs['templates_dir']

        self.source_src_dir = os.path.join(self.repository_dir, source_src_dir)
        self.assets_src_dir = os.path.join(self.repository_dir, assets_src_dir)

        self.templates_src_dir = os.path.join(self.repository_dir,
            templates_src_dir)
        branch = kwargs['branch'] if 'branch' in kwargs else None
        tag = kwargs['tag'] if 'tag' in kwargs else None

        self.branch = ''
        self.tag = ''
        if branch and self.git_repo:
            self.git_ref_type = 'branch'
            self.git_ref_val = branch
            self.branch = branch

        elif tag and self.git_repo:
            self.git_ref_type = 'tag'
            self.git_ref_val = tag
            self.tag = tag
        else:
            self.git_ref_type = 'file'
            self.git_ref_val = os.path.basename(self.uri)

        if self.git_repo:
            git_checkout(self.repository_dir, self.git_ref_type,
                self.git_ref_val)

        if "/" in self.git_ref_val:
            self.git_ref_val = self.git_ref_val.replace("/", "_")

        self.dest_root = dest
        self.dest = os.path.join(dest, self.git_ref_type, self.git_ref_val)
        self.source_dest_dir = os.path.join(self.dest)
        self.assets_dest_dir = os.path.join(self.dest, '_static')
        self._init_directories()

        self.template_globals = self._init_template_globals()

        logger.debug("""> Docfu
uri: %s
root: %s
dest: %s

>> Source
source: %s
static: %s
templates: %s

>> Dest
dest: %s
static: %s

>> Git ref
type: %s
value: %s """ % (self.uri, self.root, self.dest,
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

        if not os.path.exists(self.source_dest_dir):
            logger.debug("`os.makedirs(%s)`" % self.source_dest_dir)
            os.makedirs(self.source_dest_dir)

        logger.debug("`shutil.copytree.(%s, %s)`" %
                (self.assets_src_dir, self.assets_dest_dir))
        shutil.copytree(self.assets_src_dir, self.assets_dest_dir)

    def _init_template_globals(self):
        """ Return a dictionary of template globals to use in the
        templates. """
        return {
            'URL_ROOT': "/" + self.git_ref_type + "/" + self.git_ref_val,
            'GIT_REF_TYPE': self.git_ref_type,
            'GIT_REF': self.git_ref_val,
            'ASSETS': os.path.join('/', self.git_ref_type,
                                   self.git_ref_val, '_static'),
            'ALL_GIT_REFS': list_refs(self.dest_root),
            #'DOC_TREE': list_doc_tree(self.source_src_dir),
            'PKG': parse_package_json(
                os.path.join(self.repository_dir, 'package.json')),
            'TAG': self._tag(),
            'BRANCH': self._branch()
        }

    def _tag(self):
        if self.git_repo and not self.tag:
            if not self.tag:
                return get_git_tag(self.repository_dir)
            return self.tag
        return ""

    def _branch(self):
        if self.git_repo:
            if not self.branch:
                return get_git_branch(self.repository_dir)
            return self.branch
        return ""

    def _init_template_engine(self, **options):
        """ Return a jinja2 Environment. """
        defaults = {
            'extensions': [MarkdownJinja],
            'loader': jinja2.FileSystemLoader(self.source_src_dir),
        }

        defaults.update(options)
        return jinja2.Environment(**defaults)

    def watch(self):
        try:
            watcher = util.folder_watcher(self.source_src_dir, ['jmd', 'html'])
            while True:
                modified = next(watcher)
                if modified:
                    self.render()

        except KeyboardInterrupt:
            logger.warning("Keyboard interrupt, quitting.")
            sys.exit(0)

        except Exception as e:
            logger.critical(e.args)
            raise
            logger.warning(
                'Caught exception "{0}". Reloading.'.format(e))
        finally:
            time.sleep(.5)  # sleep to avoid cpu load

    def render(self):
        """ Render the docs found in the repository's source-dir into the
        destination dir. """
        logger.info("Rendering documents @ %s" % self.dest)

        self.source_files = sorted(self.source_files)
        for source_path in self.source_files:
            source_path_relative = source_path.replace(self.source_src_dir, "")
            if source_path_relative.endswith(".jmd") or source_path_relative.endswith(".html"):
                #with open(source_path, 'r') as source_file:
                    #source_data = source_file.read().decode('utf-8',
                    #    'replace')
                source_dest = os.path.join(self.source_dest_dir,
                    source_path.replace(self.source_src_dir, ""))
                source_name = os.path.basename(source_dest)
                self._render(source_name, source_path_relative, source_dest)

        logger.info("Documents rendered @ %s" % self.dest)

    def _render(self, name, path, dest):
        """ Render a single file. """
        logger.info("\t> Rendering document: %s --> %s" % (name, dest))
        template = self._env.get_template(path)
        #md_html = render_markdown(content)
        html = template.render(**self.template_globals)
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # make extension .html
        dest = os.path.splitext(dest)[0] + '.html'
        with open(dest, 'wb') as output:
            output.write(html.encode('utf-8'))
