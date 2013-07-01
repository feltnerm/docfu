import glob
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


#
# Git / repository utils
#
def git_clone(git_url):
    """ Clone a github url into a temp directory. Set a global object to 
    this class so it can be closed. """
    logger.debug("Cloning %s" % git_url)
    path = tmp_mk()
    git_clone_cmd = shlex.split('git clone %s %s' % (str(git_url), str(path)))
    logger.debug("%s"  % git_clone_cmd)
    retcode = subprocess.check_call(git_clone_cmd)
    return path 


def git_checkout(git_repo_path, ref_type, ref_val):
    """ Checkout the code at git_repo_path. Ref is the specific branch or 
    tag to use. """
    if ref_type == 'branch':
        git_checkout_cmd = shlex.split('git checkout %s' % str(ref_val))

    if ref_type == 'tag':
        git_checkout_cmd = shlex.split('git checkout -b %s' % str(tag))

    logger.debug("Checking out %s: %s" % (ref_type, ref_val))
    logger.debug("%s" % git_checkout_cmd)
    output = subprocess.Popen(git_checkout_cmd, cwd="%s" % str(git_repo_path)).communicate()
    logger.info(output)

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

def walk_files(path):
    """ Return a set of files found in `path`. """
    paths = set()
    logger.debug("Walking: %s" % path)
    for current, dirs, files in os.walk(path):
        for f in files:
            paths.add(os.path.join(current, f))
            logger.debug("Source file found: %s" % os.path.join(current, f))
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
        ref_types = [(x, os.path.basename(x)) for x in glob.glob(os.path.join(path, '*'))]

        for x in glob.glob(os.path.join(path, '*')):
            ref_type = os.path.basename(x)
            result[ref_type] = {}
            result[ref_type]['path'] = x
            result[ref_type]['refs'] = []
            for y in glob.glob(os.path.join(x, '*')):
                ref_value = os.path.basename(y)
                result[ref_type]['refs'].append({ 'ref_val': ref_value, 'path': y })

    return result

def list_doc_tree(path):
    """ Returns a 'tree-like' structure for navigation. """
    result = {}
    if os.path.isdir(path):
        result = { "categories": {}, "root_pages": [] }
        logger.debug("Generating doc tree for path: %s" % path)

        for x in os.listdir(path):
            if os.path.isdir(os.path.join(path, x)):
                pages = os.listdir(os.path.join(path, x))
                for page in pages:
                    base = os.path.splitext(page)[0]
                    if not base.startswith('.') and not base == 'index':
                        if x in result['categories']:
                            result['categories'][x].append(base)
                        else:
                            result['categories'][x] = [base]
            else:
                base = os.path.splitext(x)[0]
                if not base.startswith(".") and not base == 'index':
                    result['root_pages'].append(base)

        return result


