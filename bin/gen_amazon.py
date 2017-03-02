#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-13
#

"""Amazon variants."""

from __future__ import print_function, absolute_import

import json

from common import mkdata, mkvariant


SEARCH_URL = 'https://www.amazon.{tld}/gp/search?ie=UTF8&keywords={{query}}'
SUGGEST_URL = 'https://completion.amazon.{ctld}/search/complete?mkt={market}&method=completion&search-alias=aps&client=alfred-searchio&q={{query}}'


def stores():
    """Amazon variants for different stores.

    Yields:
        dict: Engine variant configuration.
    """
    data = [
        {
            'name': u'United States',
            'tld': 'com',
            'ctld': 'com',
            'market': 1,
        },
        {
            'name': u'United Kingdom',
            'tld': 'co.uk',
            'ctld': 'co.uk',
            'market': 3,
        },
        {
            'name': u'Canada',
            'tld': 'ca',
            'ctld': 'com',
            'market': 7,
        },
        {
            'name': u'Deutschland',
            'tld': 'de',
            'ctld': 'co.uk',
            'market': 4,
        },
        {
            'name': u'France',
            'tld': 'fr',
            'ctld': 'co.uk',
            'market': 5,
        },
        {
            'name': u'España',
            'tld': 'es',
            'ctld': 'co.uk',
            'market': 44551,
        },
        {
            'name': u'Brasil',
            'tld': 'com.br',
            'ctld': 'com',
            'market': 526970,
        },
    ]
    for d in data:
        # log('d=%r', d)
        s = mkvariant(d['tld'], d['name'],
                      u'Amazon {}'.format(d['name']),
                      SEARCH_URL.format(**d),
                      SUGGEST_URL.format(**d),
                      )
        yield s


def main():
    """Print Amazon engine JSON to STDOUT."""
    data = mkdata('Amazon', 'Online shopping')

    for s in stores():
        data['variants'].append(s)

    print(json.dumps(data, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
