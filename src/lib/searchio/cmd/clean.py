#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-17
#

"""searchio clean [-h|-a]

Delete stale files from the cache.

Usage:
    searchio clean [-a]
    searchio -h

Options:
    -a, --all      Delete everything in the cache
    -h, --help     Display this help message
"""

from __future__ import print_function, absolute_import

import os
from time import time

from docopt import docopt

from searchio import MAX_CACHE_AGE
from searchio import util

log = util.logger(__name__)


def usage(wf=None):
    """CLI usage instructions."""
    return __doc__


def run(wf, argv):
    """Run ``searchio clean`` sub-command."""
    from shutil import rmtree

    args = docopt(usage(wf), argv)

    # Clear old session data
    wf.clear_session_cache()

    # Clear entire cache
    if args.get('--all'):
        return wf.clear_cache()

    # Only clear state searches
    path = wf.cachefile('searches')
    if not os.path.exists(path):
        return

    def _relpath(p):
        return p.replace(path + '/', '')

    def _emptydir(p):
        files = os.listdir(p)
        if not files:
            return True
        for fn in files:
            if fn in ('.DS_Store', r'Icon\r'):
                continue
            return False

        return True

    i = 0
    for root, dirnames, filenames in os.walk(path, topdown=False):
        for fn in filenames:
            p = os.path.join(root, fn)
            age = time() - os.path.getmtime(p)
            if age > MAX_CACHE_AGE:
                log.debug('[clean/expired] %r', _relpath(p))
                os.unlink(p)
                i += 1

        for dn in dirnames:
            p = os.path.join(root, dn)
            if _emptydir(p):
                log.debug('[clean/empty] %r', _relpath(p))
                rmtree(p)
                i += 1

    log.info('[clean] %d stale item(s) deleted', i)
