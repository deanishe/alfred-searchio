#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-13
#

"""
core.py
=======

User-facing workflow functions.
"""

from __future__ import print_function, absolute_import

from hashlib import md5
import logging
import os
from time import time

from workflow import ICON_SETTINGS

from searchio import MAX_CACHE_AGE, DEFAULT_ENGINE
from searchio.engines import Manager as EngineManager
from searchio import util


log = logging.getLogger('workflow.{}'.format(__name__))


def get_defaults(wf):
    """Return default settings for variant and engine."""
    lang = wf.cached_data('system-language',
                          lambda: util.get_system_language(),
                          max_age=86400)
    params = [
        # default key, settings key, environment variable, default
        ('engine', 'default_engine', 'DEFAULT_ENGINE', DEFAULT_ENGINE),
        ('variant', 'default_variant', 'DEFAULT_VARIANT', lang)
    ]
    d = {}
    for k, sk, ek, default in params:
        v = wf.settings.get(sk, os.getenv(ek)) or default
        d[k] = wf.decode(v)

    log.debug('defaults=%r', d)
    return d


def cached_search(wf, engine, variant_id, query):

    h = md5(query.encode('utf-8')).hexdigest()
    reldir = 'searches/{}/{}/{}/{}'.format(engine.id, variant_id,
                                           h[:2], h[2:4])
    # Ensure cache directory exists
    dirpath = wf.cachefile(reldir)
    # log.debug('reldir=%r, dirpath=%r', reldir, dirpath)
    # log.debug('bundleid=%r', wf.bundleid)
    # log.debug('info=%r', wf.info)
    # log.debug('env=%r', wf.alfred_env)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    key = u'{0}/{1}'.format(reldir, h)

    def _wrapper():
        return engine.suggest(query, variant_id)

    return wf.cached_data(key, _wrapper, max_age=MAX_CACHE_AGE)
