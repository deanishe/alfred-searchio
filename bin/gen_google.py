#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-12
#

"""Generate Google JSON variants configuration based on `google-languages.tsv`"""

from __future__ import print_function, absolute_import

from collections import namedtuple
import csv
import json

from common import datapath, log, mkdata, mksearch
path = datapath('google-languages.tsv')

SEARCH_URL = 'https://www.google.com/search?q={{query}}&hl={hl}&safe=off'
SUGGEST_URL = 'https://suggestqueries.google.com/complete/search?client=firefox&q={{query}}&hl={hl}'

Lang = namedtuple('Lang', 'id name')


def langs():
    with open(path) as fp:
        for line in csv.reader(fp, delimiter='\t'):
            yield Lang(*[s.decode('utf-8') for s in line])


def main():
    data = mkdata('google', u'Google', u'Google web search',
                  icon='google.png')
    for l in langs():
        s = mksearch(u'google.{}'.format(l.id),
                     l.name,
                     u'Google ({})'.format(l.name),
                     SEARCH_URL.format(hl=l.id),
                     SUGGEST_URL.format(hl=l.id),
                     u'google.png',
                     l.id)
        data['searches'].append(s)
    # with open(path) as fp:
    #     for line in fp:
    #         line = line.decode('utf-8').strip()
    #         if not line:
    #             continue
    #         id_, name = line.split('\t')
    #         result[id_] = {'name': name, 'vars': {'hl': id_}}

    print(json.dumps(data, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
