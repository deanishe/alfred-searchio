#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-01
#

"""Searchio! search engines."""

from __future__ import print_function, unicode_literals, absolute_import

# import abc
# from collections import OrderedDict
# import imp
# import json
from operator import attrgetter
import os
# import urllib
import time

# from workflow import web

from searchio.models import Engine, JSONEngine, Search
from searchio import util

log = util.logger(__name__)

_engines = set()
_engine_dirs = set()


# TODO: Load Python files
def load(*dirpaths):
    """Import engines from JSON files in directories."""
    start = time.time()
    paths = []
    engines = []
    for dirpath in dirpaths:

        found = False
        log.debug('[engines/load/search] %s ...', dirpath)
        for root, dirnames, filenames in os.walk(dirpath):
            for fn in filenames:
                if os.path.splitext(fn)[1].lower() == '.json':
                    paths.append(os.path.join(root, fn))
                    found = True
        if found:
            _engine_dirs.add(dirpath)

    log.debug('%d JSON file(s) found', len(paths))
    for p in paths:

        e = JSONEngine(p)
        try:
            e.validate()
        except ValueError as err:
            log.error('[engines/load/error] %r : %s', err,
                      util.shortpath(p))
            continue

        log.debug('path=%s, engine=%r', p, e)
        _engines.add(e)
        # engines.append(e)
    log.debug('[engines/load] %d engine(s), %d search(es) in %0.3fs',
              len(_engines), len(searches()), time.time() - start)

    return sorted(engines, key=lambda e: e.uid)


def engines():
    """All loaded engines."""
    return sorted(Engine.instances(), key=attrgetter('title'))
    # objs = list(Engine.instances())
    # log.debug('[engines] %d engine(s) loaded', len(objs))
    # return objs


def engine(uid, default=None):
    """Get engine for UID."""
    for e in engines():
        if e.uid == uid:
            return e
    return default


# def icon(name):
#     """Find icon for name in an Engine directory."""
#     name = os.path.splitext(name)[0]
#     for dpath in _engine_dirs:
#         for n in [u'{}{}'.format(name, x) for x in IMAGE_EXTENSIONS]:
#             p = os.path.join(dpath, n)
#             if os.path.exists(p):
#                 return p


def searches():
    """All loaded searches."""
    return sorted(Search.instances(), key=attrgetter('title'))
    # objs = list(Search.instances())
    # log.debug('[engines] %d search(es) loaded', len(res))
    # return res


def search(uid, default=None):
    """Get `Search` for UID."""
    for s in searches():
        if s.uid == uid:
            return s
    return default
