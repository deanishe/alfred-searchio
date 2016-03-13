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
IMDb search as Python plugin.
"""

from __future__ import absolute_import, print_function, unicode_literals


from searchio.engines import Engine


class IMBd(Engine):
    """Get search suggestions from IMDb."""

    @property
    def id(self):
        return 'imdb'

    @property
    def name(self):
        return 'IMDb'

    @property
    def suggest_url(self):
        return 'http://sg.media-imdb.com/suggests/{query:.1}/{query}.json'

    @property
    def search_url(self):
        return 'http://www.imdb.com/find?s=all&q={query}'

    @property
    def variants(self):
        return {'*': {'name': 'Default'}}
