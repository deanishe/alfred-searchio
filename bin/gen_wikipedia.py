#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-17
#

"""Generate Wikipedia engine JSON."""

from __future__ import print_function, absolute_import

from collections import namedtuple
import json

from bs4 import BeautifulSoup as BS

from common import datapath, httpget, mkdata, mkvariant

url = 'https://meta.wikimedia.org/wiki/List_of_Wikipedias'
cachepath = datapath('Wikipedia.html')

# Ignore wikis whose article count is below...
MIN_ARTICLE_COUNT = 10000

SEARCH_URL = 'https://{l.code}.wikipedia.org/wiki/{{query}}'
SUGGEST_URL = ('https://{l.code}.wikipedia.org/w/api.php?'
               'action=opensearch&search={{query}}')

# superset of Lang
Wiki = namedtuple('Wiki', 'name code size')


def html():
    """Encoded HTML data from URL or cache (if it exists).

    Returns:
        str: Raw bytes returned from URL/file
    """
    return httpget(url, cachepath)


def parse(soup):
    """Yield `Wiki` tuples for BS soup.

    Args:
        soup (BeatifulSoup): Soup for list of Wikipedias

    Yields:
        Wiki: Extracted wikis
    """
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) != 12:  # cols in wiki list tables
            continue
        name, code, size = [cells[x].get_text() for x in range(2, 5)]
        size = int(size.replace(',', ''))
        w = Wiki(name, code, size)
        yield w


def lang2search(l):
    """Convert `Lang` to search `dict`."""
    desc = u'Wikipedia ({})'.format(l.name)
    return mkvariant(l.code.lower(),
                     l.name, desc,
                     SEARCH_URL.format(l=l),
                     SUGGEST_URL.format(l=l),
                     )


def main():
    """Print Wikipedia engine JSON to STDOUT."""
    data = mkdata(u'Wikipedia', u'Collaborative encyclopaedia', pcencode=True)

    soup = BS(html(), 'html.parser')
    for w in parse(soup):
        if w.size < MIN_ARTICLE_COUNT:
            # log('too small: %r', w.name)
            continue

        # log('wiki=%r', w)
        data['variants'].append(lang2search(w))

    print(json.dumps(data,
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
