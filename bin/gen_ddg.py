#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-02-05
#

"""Generate Duck Duck Go JSON variants configuration based on `ddg-variants.tsv`"""

from __future__ import print_function, absolute_import

from collections import namedtuple
import csv
import json

from common import datapath, log, mkdata, mkvariant
path = datapath('ddg-variants.tsv')

SEARCH_URL = 'https://duckduckgo.com/?kp=-1&kz=-1&kl={kl}&q={{query}}'
SUGGEST_URL = 'https://duckduckgo.com/ac/?kp=-1&kz=-1&kl={kl}&q={{query}}'

Variant = namedtuple('Variant', 'id name')


def variants():
    with open(path) as fp:
        for line in csv.reader(fp, delimiter='\t'):
            yield Variant(*[s.decode('utf-8') for s in line])


def main():
    data = mkdata(u'Duck Duck Go', u'Alternative search engine',
                  jsonpath='[*].phrase',)

    for v in variants():
        s = mkvariant(v.id.lower(), v.name,
                      u'Duck Duck Go {}'.format(v.name),
                      SEARCH_URL.format(kl=v.id),
                      SUGGEST_URL.format(kl=v.id),
                      # lang=l.id.lower(),
                      )
        data['variants'].append(s)
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
