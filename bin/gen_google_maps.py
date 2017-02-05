#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-02-05
#

"""Generate Google JSON variants configuration based on `google-languages.tsv`"""

from __future__ import print_function, absolute_import

from collections import namedtuple
import csv
import json

from common import datapath, log, mkdata, mkvariant
path = datapath('google-languages.tsv')

SEARCH_URL = 'https://www.google.com/maps/search/{{query}}?hl={hl}'
SUGGEST_URL = 'https://maps.googleapis.com/maps/api/place/queryautocomplete/json?input={{query}}&language={hl}&key={{GOOGLE_PLACES_API_KEY}}'

Lang = namedtuple('Lang', 'id name')


def langs():
    with open(path) as fp:
        for line in csv.reader(fp, delimiter='\t'):
            yield Lang(*[s.decode('utf-8') for s in line])


def main():
    data = mkdata(u'Google Maps', u'Location search',
                  jsonpath='predictions[*].description')
    for l in langs():
        s = mkvariant(l.id.lower(), l.name,
                      u'Google Maps ({})'.format(l.name),
                      SEARCH_URL.format(hl=l.id),
                      SUGGEST_URL.format(hl=l.id),
                      # lang=l.id.lower(),
                      )
        data['variants'].append(s)

    print(json.dumps(data, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
