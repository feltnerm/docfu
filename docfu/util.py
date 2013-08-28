import fnmatch
import glob
import json
import os
import os.path
import random
import shlex
import shutil
import subprocess
import sys
import tempfile
import urlparse
import logging

import git

logger = logging.getLogger('docfu')


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


def parse_package_json(json_path):

    pkg = None
    with open(json_path, 'r') as json_file:
        pkg = json.loads(json_file.read())
    return pkg


#
# Git / repository utils
#
def git_clone(git_url):
    """ Clone a github url into a temp directory. Set a global object to
    this class so it can be closed. """
    logger.debug("Cloning %s" % git_url)
    path = tmp_mk()
    git_clone_cmd = shlex.split('git clone %s %s' % (str(git_url), str(path)))
    logger.debug("%s" % git_clone_cmd)
    retcode = subprocess.check_call(git_clone_cmd)
    return path


def git_checkout(git_repo_path, ref_type, ref_val):
    """ Checkout the code at git_repo_path. Ref is the specific branch or
    tag to use. """
    if ref_type == 'branch':
        git_checkout_cmd = shlex.split('git checkout %s' % str(ref_val))

    if ref_type == 'tag':
        git_checkout_cmd = shlex.split('git checkout -b %s' % str(ref_val))

    logger.debug("Checking out %s: %s" % (ref_type, ref_val))
    logger.debug("%s" % git_checkout_cmd)
    output = subprocess.Popen(git_checkout_cmd,
        cwd="%s" % str(git_repo_path)).communicate()
    logger.info(output)


def get_git_tag(git_repo_path):
    repo = git.Repo(git_repo_path)
    g = repo.git
    tag = g.describe('--tags', g.rev_list('--tags', max_count=1))
    return tag


def get_git_branch(git_repo_path):
    cmd = shlex.split("git rev-parse --abbrev-ref HEAD")
    logger.debug("Getting git branch: %s" % cmd)
    p = subprocess.Popen(cmd, cwd="%s" % str(git_repo_path),
        stdout=subprocess.PIPE)
    out, err = p.communicate()
    if out and not err:
        logger.debug("Branch: %s" % out)
        return out
    logger.error("%s" % err)
    return ''


#
# Temporary File / Directory Utilities
#
def tmp_mk():
    """ Make a temporary directory, already prefixed with `docfu-`,
    in `/tmp/`."""
    if not os.path.isdir(os.path.expanduser("~/tmp")):
        os.makedirs(os.path.expanduser("~/tmp"))
    path = tempfile.mkdtemp(prefix='docfu-', dir=os.path.expanduser('~/tmp'))
    logger.debug("Temporary path created at: %s" % path)
    return path


def tmp_close(path):
    """ Remove the directory denoted by `path`. """
    try:
        shutil.rmtree(path)
        logger.debug("Temporary path removed at: %s" % path)
    except Exception, e:
        if e.errno != 2:
            logger.error("Cannot remove temporary path %s. Error %s"
                % (path, e))
            raise


def tmp_cp(src):
    """ Copy the source directory to a tmp directory.

    @TODO: ignore version control and other things.
    """
    dest = tmp_mk()
    dest = os.path.join(os.path.expanduser("~"), 'tmp',
        'docfu-%s' % random.randint(999, 10000))
    shutil.copytree(src, dest,
        ignore=shutil.ignore_patterns('*.git', 'node_modules'))
    logger.debug("Copied source files %s to tempdir %s" % (src, dest))
    return dest


def walk_files(path):
    """ Return a set of files found in `path`. """
    paths = set()
    logger.debug("Walking: %s" % path)
    for current, dirnames, files in os.walk(path):
        dirnames[:] = filter(lambda x: not (x.startswith("_") or x.startswith(".")), dirnames)
        for f in files:
            if not (f.startswith("_") or f.startswith(".")):
                paths.add(os.path.join(current, f))
                logger.debug("Source file found: %s" %
                    os.path.join(current, f))
    return paths


def list_refs(path):
    """ Return the list of branches/tags found in the root `path`.
    We assume the folder structure is like so:
        `<root>[/<ref_type>[/<ref_name>]]`
    {
        <ref_type> :
            {
                <path>: '',
                <refs>: [
                    {
                        <ref_val>: '',
                        <path>: ''
                    },
                ],
            },
    }
    """
    result = {}
    if os.path.isdir(path):
        logger.debug("Listing refs for root path: %s" % path)

        for x in glob.glob(os.path.join(path, '*')):
            ref_type = os.path.basename(x)
            result[ref_type] = {}
            result[ref_type]['path'] = x
            result[ref_type]['refs'] = []
            for y in glob.glob(os.path.join(x, '*')):
                if os.path.isdir(y):
                    ref_value = os.path.basename(y)
                    result[ref_type]['refs'].append({
                        'ref_val': ref_value,
                        'path': y
                    })

    return result


def list_doc_tree(root_path):
    """ Returns a 'tree-like' structure for navigation. """
    # (name, relpath, sub)
    doctree = []

    def recurse_doc_tree(item_path):
        result = []
        item_sub_dirs = []
        item_sub_files = []
        item_name = os.path.basename(item_path)
        item_dir = os.path.dirname(item_path)
        if os.path.isdir(item_path):
            for name in os.listdir(item_path):
                if not name.startswith(".") and name != 'index.html':
                    if os.path.isdir(os.path.join(item_path, name)):
                            item_sub_dirs.append(
                                recurse_doc_tree(os.path.join(item_path,
                                                              name)))

                    elif os.path.isfile(os.path.join(item_path, name)):
                        item_sub_files.append({
                            'name': os.path.splitext(name)[0],
                            'path': item_path.replace(root_path, "")
                        })

        result = {
            'name': os.path.splitext(item_name)[0],
            'path': item_path.replace(root_path, "")
        }
        if len(item_sub_dirs) > 0:
            result['dirs'] = item_sub_dirs
        if len(item_sub_files) > 0:
            result['files'] = item_sub_files
        return result

    for item_name in os.listdir(root_path):
        if not item_name.startswith(".") and item_name != 'index.html':
            doctree.append(
                recurse_doc_tree(os.path.join(root_path,
                                              item_name)))
    return doctree

def folder_watcher(path, extensions, ignores=[]):
    '''Generator for monitoring a folder for modifications.

    Returns a boolean indicating if files are changed since last check.
    Returns None if there are no matching files in the folder'''

    def file_times(path):
        '''Return `mtime` for each file in path'''

        for root, dirs, files in os.walk(path):
            dirs[:] = [x for x in dirs if not x.startswith(os.curdir)]

            for f in files:
                if (f.endswith(tuple(extensions)) and
                    not any(fnmatch.fnmatch(f, ignore) for ignore in ignores)):
                    try:
                        yield os.stat(os.path.join(root, f)).st_mtime
                    except OSError as e:
                        logger.warning('Caught Exception: {}'.format(e))

    LAST_MTIME = 0
    while True:
        try:
            mtime = max(file_times(path))
            if mtime > LAST_MTIME:
                LAST_MTIME = mtime
                yield True
        except ValueError:
            yield None
        else:
            yield False

    #matches = {}
    #for p, dirs, files in os.walk(path):
    #    name = os.path.basename(p)
    #    relpath = p.replace(path, "")
    #    files2 = []
    #    for f in files:
    #        if not f.startswith("."):
    #            fname = os.path.splitext(os.path.basename(f))[0]
    #            fpath = os.path.join(relpath, f)
    #            files2.append((fname, fpath))

    #    matches.setdefault(p,[]).append(os.path.join)
    #    result.append((name, relpath, files2))
    #return result
