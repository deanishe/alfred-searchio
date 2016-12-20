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
Searchio!
=========

Alfred 3 search suggestion workflow.
"""

from __future__ import print_function, absolute_import


DEFAULT_ENGINE = 'google'

UPDATE_SETTINGS = {'github_slug': 'deanishe/alfred-searchio'}
HELP_URL = 'https://github.com/deanishe/alfred-searchio/issues'

# Cache search results for 15 minutes
MAX_CACHE_AGE = 900

IMAGE_EXTENSIONS = [
    '.png',
    '.icns',
    '.jpg',
    '.jpeg',
    '.gif',
]
