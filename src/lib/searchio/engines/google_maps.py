#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-17
#

"""Google Places search as Python plugin."""

from __future__ import absolute_import, print_function

import os

from searchio.engines import Engine
from searchio.engines._google import LANGUAGES

_error_msg = """\
GOOGLE_PLACES_APIKEY not set

The Google Maps search requires an API key for the
Google Places API.

You can get a key from:
https://developers.google.com/places/web-service/autocomplete

Then set GOOGLE_PLACES_APIKEY in the workflow configuration
sheet.
"""


class GoogleMaps(Engine):
    """Get search suggestions from Google Maps."""

    @property
    def id(self):
        return 'google-maps'

    @property
    def name(self):
        return 'Google Maps'

    @property
    def suggest_url(self):
        key = os.getenv('GOOGLE_PLACES_APIKEY')
        if not key:
            raise RuntimeError(_error_msg)

        return 'https://maps.googleapis.com/maps/api/place/queryautocomplete/json?input={query}&language={hl}&key=' + key

    @property
    def search_url(self):
        return 'https://www.google.com/maps/search/{query}?hl={hl}'

    def _post_process_response(self, response_data):
        suggestions = []
        for d in response_data.get('predictions', []):
            suggestions.append(d.get('description'))
        return suggestions
        # return response_data[1]

    @property
    def variants(self):
        v = {}
        for lang, name in LANGUAGES.items():
            v[lang] = {
                'name': name,
                'vars': {'hl': lang}
            }
        return v
        # return {
        #     'en': {
        #         'name': 'English',
        #         'vars': { 'hl': 'en' },
        #     },
        #     'de': {
        #         'name': 'Deutsch',
        #         'vars': { 'hl': 'de' },
        #     },
        # }
