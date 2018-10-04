#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-09
#

"""Generate Wikia engine JSON."""

from __future__ import print_function, absolute_import

from collections import namedtuple
import json
import re
import sys

from bs4 import BeautifulSoup as BS

from common import datapath, httpget, mkdata, mkvariant

SOURCES = [
    ('http://community.wikia.com/wiki/Hub:Big_wikis',
     datapath('Wikia-Biggest.html')),
    ('http://community.wikia.com/wiki/Hub:Wikis_with_many_active_members',
     datapath('Wikia-Most-Active.html')),
    ('http://community.wikia.com/wiki/Hub:Sci-Fi',
     datapath('Wikia-SF.html')),
]

SEARCH_URL = 'http://{w.subdomain}.wikia.com/wiki/{{query}}'
SUGGEST_URL = ('http://{w.subdomain}.wikia.com/api.php?'
               'action=opensearch&search={{query}}')


Wiki = namedtuple('Wiki', 'name subdomain')

match = re.compile(r'http://(.+?)\..+').match


def log(s, *args):
    """Simple STDERR logger."""
    if args:
        s = s % args
    print(s, file=sys.stderr)


def html(url, cachepath):
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
    css_classes = ('nostar', 'yellowstar', 'orangestar',
                   'redstar', 'greenstar')
    divs = []
    for c in css_classes:
        divs.extend(soup.find_all('div', c))

    links = []
    for d in divs:
        links.extend(d.find_all('a', 'extiw'))

    for link in links:
        url = link.get('href')
        title = link.get_text()
        if not url:
            log('[ERROR] no URL: %r', link)
            continue
        if not title:
            log('[ERROR] no title: %r', link)
            continue

        m = match(url)
        if not m:
            log('[ERROR] no subdomain found: %r', url)
            continue

        subdomain = m.group(1)
        yield Wiki(title, subdomain)


def wiki2search(w):
    """Convert `Lang` to search `dict`."""
    desc = u'{} (Wikia)'.format(w.name)
    return mkvariant(w.subdomain.lower(),
                     w.name, desc,
                     SEARCH_URL.format(w=w),
                     SUGGEST_URL.format(w=w),
                     )


def main():
    """Print Wikipedia engine JSON to STDOUT."""
    data = mkdata(u'Wikia', u'Fandom sites', pcencode=True)

    wikis = {}
    i = 0
    for url, cachepath in SOURCES:
        soup = BS(html(url, cachepath), 'html.parser')
        for w in parse(soup):
            # log('wiki=%r', w)
            i += 1
            # log(u'[%03d] "%s" (%s)', i, w.name, w.subdomain)
            wikis[w.subdomain] = w

    wikis = wikis.values()

    wikis.sort(key=lambda t: t.name)
    data['variants'] = [wiki2search(w) for w in wikis]

    print(json.dumps(data,
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
