#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-01
#

"""
"""

from __future__ import print_function, unicode_literals


from engines import Engine


class Google(Engine):
    """Get search suggestions from Google."""

    @property
    def id(self):
        return 'googlepy'

    @property
    def name(self):
        return 'GooglePy'

    @property
    def suggest_url(self):
        return 'https://suggestqueries.google.com/complete/search?client=firefox&q={query}&hl={variant}'

    @property
    def search_url(self):
        return 'https://www.google.com/search?q={query}&hl={hl}&safe=off'

    @property
    def variants(self):
        return {
            'en': {
                'name': 'English',
                'vars': { 'hl': 'en' },
            },
            'de': {
                'name': 'Deutsch',
                'vars': { 'hl': 'de' },
            },
        }
