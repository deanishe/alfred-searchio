#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-02-05
#

"""Generate Google Maps engine JSON.

Suggestions are based on the Google Places API, which
requires an API key :(
"""

from __future__ import print_function, absolute_import

from google import google_search

SEARCH_URL = 'https://www.google.com/maps/search/{{query}}?hl={hl}'
SUGGEST_URL = 'https://maps.googleapis.com/maps/api/place/queryautocomplete/json?input={{query}}&language={hl}&key=${{GOOGLE_PLACES_API_KEY}}'
JSON_PATH = '$.predictions[*].description'

if __name__ == '__main__':
    google_search(SEARCH_URL, SUGGEST_URL, u'Google Maps', u'Location search',
                  jsonpath=JSON_PATH)
