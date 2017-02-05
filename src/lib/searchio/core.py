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

IMAGE_EXTS = ['png', 'icns', 'jpg', 'jpeg']


class Context(object):
    """Program helper functions and variables.

    Attributes:
        wf (workflow.Workflow3): Current workflow object.
    """
    def __init__(self, wf):
        self.wf = wf
        self._icon_finder = None
        # self._engine_finder = None

    def icon(self, name):
        if not self._icon_finder:
            self._icon_finder = util.FileFinder(self.icon_dirs, IMAGE_EXTS)

        return self._icon_finder.find(name, 'icon.png')

    def search(self, uid):
        return self.wf.datafile('searches/{}.json'.format(uid))

    # def engine(self, uid):
    #     if not self._engine_finder:
    #         self._engine_finder = util.FileFinder(self.engine_dirs, ['json'])

    #     return self._engine_finder.find(uid)

    @property
    def engine_dirs(self):
        return [
            os.path.join(os.path.dirname(__file__), 'engines'),
            self.wf.datafile('engines'),
        ]

    @property
    def icon_dirs(self):
        return [
            self.wf.datafile('icons'),
            self.wf.workflowfile('icons/engines'),
            self.wf.workflowfile('icons'),
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
