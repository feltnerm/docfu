#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement

import argparse
import logging
import sys

from docfu import log
from docfu import Docfu
from docfu import docfu_figlet


def parse_args(argv):
    """ Parse command line arguments. """

    argp = argparse.ArgumentParser(
        prog="docfu",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=docfu_figlet)

    argp.add_argument('-c', '--config',
        help='An [optional] configuration file to read.')

    argp.add_argument('-b', '--branch',
        help='A git branch to checkout.')

    argp.add_argument('-t', '--tag',
        help='A git tag to checkout.')

    argp.add_argument('-r', '--root-dir',
        default='docs/',
        help='Root directory which docs are built from.')

    argp.add_argument('--assets-dir',
        default='docs/_static',
        help='Directory to look for assets (css, js & images) in.')

    argp.add_argument('--source-dir',
        default='docs/',
        help='Source directory which to compile from.')

    argp.add_argument('--temp-dir',
        default='/tmp/',
        help='Temporary directory to build docs')

    argp.add_argument('--templates-dir',
        default='docs/_templates',
        help='Directory to look for Jinja2 templates in.')

    argp.add_argument('uri',
        nargs=1,
        help='A URI to a file path, git repository, or github repo.')

    argp.add_argument('destination',
        nargs=1,
        help='Destination for compiled source.')

    argp.add_argument('-l', '--log-file', help='File to log to.')

    argp.add_argument('-V', '--version', action='store_const', const=True,
        default=False, dest='version', help="Output verison")

    argp.add_argument('-v', '--verbose',
        action='store_const',
        const=logging.INFO,
        dest='verbosity',
        help='Run verbosely or not.')

    argp.add_argument('-d', '--debug',
        action='store_const',
        const=logging.DEBUG,
        dest='verbosity',
        help='Run debugly or not.')

    argp.add_argument('-q', '--quiet',
        action='store_const',
        const=logging.CRITICAL,
        dest='verbosity',
        help='Run quietly or not.')

    argp.add_argument('--dev',
         action='store_const',
         const=True,
         default=False,
         help='Run in production mode or not (send emails on error)')

    options = argp.parse_args(argv)

    return vars(options)


def main(argv=None):
    """ Main """

    if not argv:
        argv = sys.argv[1:]

    options = parse_args(argv)
    uri = options.get('uri')[0]
    dest = options.get('destination')[0]
    root = options.get('root_dir')
    del options['uri']
    del options['destination']
    del options['root_dir']

    if options.get('version', False):
        from docfu import __version__
        print("v" + __version__)
        return 0

    logger = log.init(level=options.get('verbosity', logging.DEBUG),
        development=options.get('dev', False))

    with Docfu(uri, root, dest, **options) as df:
        df()

    return 0  # success

if __name__ == '__main__':
    STATUS = main()
    sys.exit(STATUS)
