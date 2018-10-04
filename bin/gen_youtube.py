#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-19
#

"""Generate YouTube variants."""

from __future__ import print_function, absolute_import

from collections import namedtuple
import json
import re

from bs4 import BeautifulSoup as BS

from common import (
    datapath, log,
    mkdata, mkvariant, sanitise_ws,
)

cachepath = datapath('YouTube.html')

SEARCH_URL = ('https://www.youtube.com/results?'
              'gl={y.country}&persist_gl=1&search_query={{query}}')
SUGGEST_URL = ('https://suggestqueries.google.com/complete/search?'
               'client=firefox&ds=yt&hl={y.lang}&q={{query}}')

# superset of Lang
YT = namedtuple('YT', 'name lang country')


def html():
    """Encoded HTML data from URL or cache (if it exists).

    Returns:
        str: Raw bytes returned from URL/file
    """
    with open(cachepath) as fp:
        return fp.read()


def parse(soup):
    """Yield `YT` tuples for BS soup.

    Args:
        soup (BeatifulSoup): Soup for list of Wikipedias

    Yields:
        tuple: Extracted `YT` tuples
    """
    for a in soup.find_all('a', class_='yt-picker-item'):
        # log('a=%r', a)
        m = re.match(r'.+\?gl=([A-Z]+).*', a['href'])
        if not m:
            log('no region: %r', a['href'])
            continue
        country = lang = m.group(1).lower()
        name = sanitise_ws(a.get_text())
        yield YT(name, lang, country)


def yt2search(y):
    """Convert `YT` to search `dict`."""
    uid = u'youtube.{}'.format(y.country)
    desc = u'YouTube ({})'.format(y.name)
    return mkvariant(y.country.lower(),
                     y.name, desc,
                     SEARCH_URL.format(y=y),
                     SUGGEST_URL.format(y=y),
                     )


def main():
    data = mkdata(u'YouTube', u'Video search')

    soup = BS(html(), 'html.parser')
    for y in parse(soup):
        data['variants'].append(yt2search(y))

    print(json.dumps(data,
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
