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

SEARCH_URL = 'https://www.google.com/search?tbm=isch&q={{query}}&hl={hl}&safe=off'
SUGGEST_URL = 'https://suggestqueries.google.com/complete/search?client=firefox&ds=i&q={{query}}&hl={hl}&safe=off'

Lang = namedtuple('Lang', 'id name')


def langs():
    with open(path) as fp:
        for line in csv.reader(fp, delimiter='\t'):
            yield Lang(*[s.decode('utf-8') for s in line])


def main():
    data = mkdata(u'Google Images', u'Image search',
                  jsonpath='predictions[].description')
    for l in langs():
        s = mkvariant(l.id.lower(), l.name,
                      u'Google Images ({})'.format(l.name),
                      SEARCH_URL.format(hl=l.id),
                      SUGGEST_URL.format(hl=l.id),
                      # lang=l.id.lower(),
                      )
        data['variants'].append(s)

    print(json.dumps(data, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
