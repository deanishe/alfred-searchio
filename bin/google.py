#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-02-06
#

"""Generate engine JSON for a Google search."""

from __future__ import print_function, absolute_import

from collections import namedtuple
import csv
import json

from common import datapath, mkdata, mkvariant

path = datapath('google-languages.tsv')

Lang = namedtuple('Lang', 'id name')


def langs():
    """All languages supported by Google.

    Yields:
        Lang: Google languages
    """
    with open(path) as fp:
        for line in csv.reader(fp, delimiter='\t'):
            yield Lang(*[s.decode('utf-8') for s in line])


def google_search(search_url, suggest_url, title, description, jsonpath=None):
    """Generate an engine definition for a Google search.

    Args:
        search_url (str): Search URL template
        suggest_url (str): Suggest URL template
        title (unicode): Engine title
        description (unicode): Engine description
        jsonpath (unicode, optional): JSONPath for results

    """
    kwargs = {}
    if jsonpath:
        kwargs['jsonpath'] = jsonpath

    data = mkdata(title, description, **kwargs)

    for l in langs():
        s = mkvariant(l.id.lower(), l.name,
                      u'{} ({})'.format(title, l.name),
                      search_url.format(hl=l.id),
                      suggest_url=suggest_url.format(hl=l.id),
                      # lang=l.id.lower(),
                      )
        data['variants'].append(s)

    print(json.dumps(data, sort_keys=True, indent=2))
