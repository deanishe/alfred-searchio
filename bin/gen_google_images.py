#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-02-05
#

"""Generate Google Image engine JSON."""

from __future__ import print_function, absolute_import

from google import google_search

SEARCH_URL = 'https://www.google.com/search?tbm=isch&q={{query}}&hl={hl}&safe=off'
SUGGEST_URL = 'https://suggestqueries.google.com/complete/search?client=firefox&ds=i&q={{query}}&hl={hl}&safe=off'


if __name__ == '__main__':
    google_search(SEARCH_URL, SUGGEST_URL, u'Google Images', u'Image search')
