#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-02-05
#

"""Generate eBay engine JSON."""

from __future__ import print_function, absolute_import

from collections import namedtuple
import csv
import json

from common import datapath, mkdata, mkvariant
path = datapath('ebay-variants.tsv')

SEARCH_URL = 'https://www.ebay.{tld}/sch/i.html?_nkw={{query}}'
SUGGEST_URL = 'https://autosug.ebay.com/autosug?fmt=osr&sId={site}&kwd={{query}}'

Variant = namedtuple('Variant', 'site uid tld name')


def variants():
    """International eBay variants.

    Yields:
        Variant: eBay variant
    """
    with open(path) as fp:
        for line in csv.reader(fp, delimiter='\t'):
            yield Variant(*[s.decode('utf-8') for s in line])


def main():
    """Print eBay engine JSON to STDOUT."""
    data = mkdata(u'eBay', u'Online auction search')
    for v in variants():
        s = mkvariant(v.uid.lower(),
                      v.name,
                      u'eBay {}'.format(v.name),
                      SEARCH_URL.format(tld=v.tld),
                      SUGGEST_URL.format(site=v.site),
                      )
        data['variants'].append(s)

    print(json.dumps(data, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
