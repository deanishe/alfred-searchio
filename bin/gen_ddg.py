#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-02-05
#

"""Generate Duck Duck Go engine JSON."""

from __future__ import print_function, absolute_import

from collections import namedtuple
import csv
import json

from common import datapath, mkdata, mkvariant
path = datapath('ddg-variants.tsv')

SEARCH_URL = 'https://duckduckgo.com/?kp=-1&kz=-1&kl={kl}&q={{query}}'
SUGGEST_URL = 'https://duckduckgo.com/ac/?kp=-1&kz=-1&kl={kl}&q={{query}}'

Variant = namedtuple('Variant', 'id name')


def variants():
    """DDG variants from `ddg-variants.tsv`.

    Yields:
        Variant: DDG variant
    """
    with open(path) as fp:
        for line in csv.reader(fp, delimiter='\t'):
            yield Variant(*[s.decode('utf-8') for s in line])


def main():
    """Print DDG engine JSON to STDOUT."""
    data = mkdata(u'Duck Duck Go', u'Alternative search engine',
                  jsonpath='$[*].phrase',)

    for v in variants():
        s = mkvariant(v.id.lower(), v.name,
                      u'Duck Duck Go {}'.format(v.name),
                      SEARCH_URL.format(kl=v.id),
                      SUGGEST_URL.format(kl=v.id),
                      )
        data['variants'].append(s)

    print(json.dumps(data, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
