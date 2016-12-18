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

import logging
import os

from searchio import DEFAULT_ENGINE
from searchio import util


log = logging.getLogger('workflow.{}'.format(__name__))


def get_icon(wf, name):
    return wf.workflowfile('icons/{}.png'.format(name))


def icon_maker(wf):
    def _getter(name):
        return get_icon(wf, name)
    return _getter


def get_engine_manager(wf):
    """Return `searchio.engines.EngineManager`."""
    import searchio.engines
    engine_dirs = [os.path.dirname(searchio.engines.__file__)]
    em = searchio.engines.Manager(engine_dirs)
    return em


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
