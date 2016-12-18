#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-17
#

"""Search suggestions from Duck Duck Go."""

from __future__ import print_function, absolute_import

from searchio.engines import Engine

REGIONS = {
    'ar-es': u'Argentina',
    'at-de': u'Austria',
    'au-en': u'Australia',
    'be-fr': u'Belgium (fr)',
    'be-nl': u'Belgium (nl)',
    'bg-bg': u'Bulgaria',
    'br-pt': u'Brazil',
    'ca-en': u'Canada',
    'ca-fr': u'Canada (fr)',
    'ch-de': u'Switzerland (de)',
    'ch-fr': u'Switzerland (fr)',
    'ch-it': u'Switzerland (it)',
    'cl-es': u'Chile',
    'cn-zh': u'China',
    'co-es': u'Colombia',
    'ct-ca': u'Catalonia',
    'cz-cs': u'Czech Republic',
    'de-de': u'Germany',
    'dk-da': u'Denmark',
    'ee-et': u'Estonia',
    'es-ca': u'Spain (ca)',
    'es-es': u'Spain',
    'fi-fi': u'Finland',
    'fr-fr': u'France',
    'gr-el': u'Greece',
    'hk-tzh': u'Hong Kong',
    'hr-hr': u'Croatia',
    'hu-hu': u'Hungary',
    'id-en': u'Indonesia (en)',
    'id-id': u'Indonesia',
    'ie-en': u'Ireland',
    'il-he': u'Israel',
    'in-en': u'India',
    'it-it': u'Italy',
    'jp-jp': u'Japan',
    'kr-kr': u'Korea',
    'lt-lt': u'Lithuania',
    'lv-lv': u'Latvia',
    'mx-es': u'Mexico',
    'my-en': u'Malaysia (en)',
    'my-ms': u'Malaysia',
    'nl-nl': u'Netherlands',
    'no-no': u'Norway',
    'nz-en': u'New Zealand',
    'pe-es': u'Peru',
    'ph-en': u'Philippines',
    'ph-tl': u'Philippines (tl)',
    'pl-pl': u'Poland',
    'pt-pt': u'Portugal',
    'ro-ro': u'Romania',
    'ru-ru': u'Russia',
    'se-sv': u'Sweden',
    'sg-en': u'Singapore',
    'sk-sk': u'Slovakia',
    'sl-sl': u'Slovenia',
    'th-th': u'Thailand',
    'tr-tr': u'Turkey',
    'tw-tzh': u'Taiwan',
    'ua-uk': u'Ukraine',
    'uk-en': u'United Kingdom',
    'us-en': u'United States',
    'us-es': u'United States (es)',
    'vn-vi': u'Vietnam',
    'wt-wt': u'All Results',
    'xa-ar': u'Saudi Arabia',
    'xa-en': u'Saudi Arabia (en)',
    'xl-es': u'Latin America',
    'za-en': u'South Africa',
}


class DuckDuckgo(Engine):
    """Search suggestions from Duck Duck Go."""

    @property
    def title_scheme(self):
        """Scheme for "Engine name (variant name)"."""
        return u'{engine.name} ({variant.name})'

    @property
    def id(self):
        return 'ddg'

    @property
    def name(self):
        return 'Duck Duck Go'

    @property
    def suggest_url(self):
        return 'https://duckduckgo.com/ac/?kp=-1&kz=-1&kl={region}&q={query}'

    @property
    def search_url(self):
        return 'https://duckduckgo.com/?kp=-1&kz=-1&kl={region}&q={query}'

    def _post_process_response(self, response_data):
        return [d.get('phrase') for d in response_data]

    @property
    def variants(self):
        v = {}
        for region, name in REGIONS.items():
            v[region] = {
                'name': name,
                'vars': {
                    'region': region,
                }
            }
        return v
