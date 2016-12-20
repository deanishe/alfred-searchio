#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-13
#

"""User-facing workflow functions."""

from __future__ import print_function, absolute_import

import os

from searchio import DEFAULT_ENGINE
from searchio import util

log = util.logger(__name__)


class Context(object):
    """Wrap workflow in program helper functions.

    Attributes:
        wf (workflow.Workflow3): Current workflow object.
    """
    def __init__(self, wf):
        self.wf = wf

    def icon(self, name):
        return self.wf.workflowfile('icons/{}.png'.format(name))

    # TODO: Right data model for data directory/saved searches
    @property
    def engine_dirs(self):
        return [
            os.path.join(os.path.dirname(__file__), 'engines'),
            self.wf.datafile('engines'),
        ]

    @property
    def searches_dir(self):
        return self.wf.datafile('searches')
    # TODO: defaults


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
