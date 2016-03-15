#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-13
#

"""
Get list of Wikia sites.
"""

from __future__ import print_function, unicode_literals, absolute_import

from HTMLParser import HTMLParser
from multiprocessing.dummy import Pool
import os
import re
import sys

from common import fetch_page, log

# List of biggest Wikia wikis in wikisyntax
URL = 'http://s23.org/wikistats/wikia_wiki.php?lines=30000'


def fetch_wiki(subdomain):
    url = 'http://{0}.wikia.com/'.format(subdomain)
    cachepath = os.path.join(os.path.join(
        os.path.dirname(__file__), 'wikia-pages'),
        '{0}.html'.format(subdomain))

    return fetch_page(url, cachepath)


def main():
    # search = re.compile(r'http://(.+?)\.wikia\.com/').search
    parser = HTMLParser()
    cachepath = os.path.join(os.path.dirname(__file__), 'wikia.html')
    html = fetch_page(URL, cachepath).decode('utf-8')

    matches = re.findall(r'http://([A-Za-z0-9.-]+)\.wikia\.com/', html)
    wikis = set(matches)
    # wikis2 = set(re.findall(r'http://(.+?)\.wikia\.com/', html))
    log('{0:d} wikis found'.format(len(wikis)))
    # print('{0:d} wikis found'.format(len(wikis2)))
    # diff = wikis2 - wikis
    # for n in diff:
    #     print(n)
    pool = Pool(5)
    futures = []
    total = len(wikis)
    for wiki in sorted(wikis):
        log('Queuing {0} for retrieval ...'.format(wiki))
        fut = pool.apply_async(fetch_wiki, (wiki,))
        futures.append((wiki, fut))

    pool.close()
    i = 0
    while len(futures):
        temp = []
        for wiki, fut in futures:
            if not fut.ready():
                temp.append((wiki, fut))
                continue
            i += 1
            log('[{0:04d}/{1}] {2} ...'.format(i, total, wiki))
            html = fut.get().decode('utf-8')

            # m = re.search(r'<title>(.+?)</title>', html)
            m = re.search(r'<link rel="search".+? title="(.+?)"', html)
            if not m:
                log('No title found for {0}.'.format(wiki))
                continue
            title = parser.unescape(m.group(1))

            m = re.match(r'(.+?) \(([A-Za-z-]+?)\)', title)
            if not m:
                log('Could not parse title/languages : {0!r}'.format(title))
                continue

            title, language = [s.strip() for s in m.groups()]

            # if title.endswith(' - Wikia'):
            #     title = title[:-len(' - Wikia')]

            print('{0}.wikia.com\t{1}\t{2}'.format(wiki, title, language).encode('utf-8'))
            sys.stdout.flush()

        futures = temp

    pool.join()


if __name__ == '__main__':
    main()
