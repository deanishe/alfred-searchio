#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-19
#

"""Saved search configurations."""

from __future__ import print_function, absolute_import

import json
import os

from searchio import util

log = util.logger(__name__)


class Manager(object):

    def __init__(self, dirpath):
        self.dirpath = dirpath

    def get(self, uid, default=None):
        p = self._fpath(uid)
        if not os.path.exists(p):
            return default
        with open(p) as fp:
            return json.load(fp)

    def _fpath(self, uid):
        return os.path.join(self.dirpath, uid + '.json')

    def save(self, title, search_url, uid, suggest_url='', icon=''):
        d = dict(title=title, search_url=search_url,
                 suggest_url=suggest_url, uid=uid, icon=icon)
        p = self._fpath(uid)
        with open(p, 'wb') as fp:
            json.dump(d, fp, sort_keys=True, indent=2)

        log.debug('[search/save] %r to %r', title, p)
