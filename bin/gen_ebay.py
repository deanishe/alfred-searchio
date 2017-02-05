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
path = datapath('ebay-variants.tsv')

# SEARCH_URL = 'https://www.google.com/search?q={{query}}&hl={hl}&safe=off'
SEARCH_URL = 'https://www.ebay.{tld}/sch/i.html?_nkw={{query}}'
# SUGGEST_URL = 'https://suggestqueries.google.com/complete/search?client=firefox&q={{query}}&hl={hl}'
SUGGEST_URL = 'https://autosug.ebay.com/autosug?fmt=osr&sId={site}&kwd={{query}}'

Variant = namedtuple('Variant', 'site uid tld name')


def variants():
    with open(path) as fp:
        for line in csv.reader(fp, delimiter='\t'):
            yield Variant(*[s.decode('utf-8') for s in line])


def main():
    data = mkdata(u'eBay', u'Online auction search')
    for v in variants():
        s = mkvariant(v.uid.lower(),
                      v.name,
                      u'eBay {}'.format(v.name),
                      SEARCH_URL.format(tld=v.tld),
                      SUGGEST_URL.format(site=v.site),
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
