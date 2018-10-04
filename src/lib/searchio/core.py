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
        """Create new `Context` for Workflow."""
        self.wf = wf
        self._icon_finder = None
        for name in ['engines', 'searches', 'icons', 'backups']:
            p = wf.datafile(name)
            if not os.path.exists(p):
                os.makedirs(p)

    def icon(self, name):
        if not self._icon_finder:
            self._icon_finder = util.FileFinder(self.icon_dirs, IMAGE_EXTS)

        return self._icon_finder.find(name, 'icon.png')

    def search(self, uid):
        """Path to search configuration for UID.

        The path may or may not exist.

        Args:
            uid (str): Search UID.

        Returns:
            str: Path to search config file.

        """
        return self.wf.datafile('searches/{}.json'.format(uid))

    def getbool(self, key, default=False):
        """Get a workflow variable as a boolean.

        ``1``, ``yes`` and ``on`` evaluate to ``True``;
        ``0``, ``no`` and ``off`` evaluate to ``False``.

        Args:
            key (str): Name of variable
            default (bool, optional): Value to return if variable is
                unset or empty.

        Returns:
            bool: Value of variable or `default`

        """
        v = os.getenv(key)
        if not v:
            return default

        if v.lower() in ('1', 'yes', 'on'):
            return True

        if v.lower() in ('0', 'no', 'off'):
            return False

        log.warning('Invalid value for "%s": %s', key, v)
        return default

    @property
    def backup_dir(self):
        """Directory to save ``info.plist`` backups to."""
        return self.wf.datafile('backups')

    @property
    def engine_dirs(self):
        """Directories to search for engine configurations."""
        return [
            os.path.join(os.path.dirname(__file__), 'engines'),
            self.wf.datafile('engines'),
        ]

    @property
    def icon_dirs(self):
        """Directories to search for icons."""
        return [
            self.wf.datafile('icons'),
            self.wf.datafile('engines'),
            self.wf.workflowfile('icons/engines'),
            self.wf.workflowfile('icons'),
        ]

    @property
    def searches_dir(self):
        """Directory to search for search configs."""
        return self.wf.datafile('searches')


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
