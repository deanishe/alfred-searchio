#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-12
#

"""Generate Google web engine JSON."""

from __future__ import print_function, absolute_import

from google import google_search

SEARCH_URL = 'https://www.google.com/search?q={{query}}&hl={hl}&safe=off'
SUGGEST_URL = 'https://suggestqueries.google.com/complete/search?client=firefox&q={{query}}&hl={hl}'


if __name__ == '__main__':
    google_search(SEARCH_URL, SUGGEST_URL, u'Google', u'General web search')
