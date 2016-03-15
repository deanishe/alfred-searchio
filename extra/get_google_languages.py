#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-12
#

"""
Generate TSV of the languages supported by Google.
"""

from __future__ import print_function, unicode_literals, absolute_import

from HTMLParser import HTMLParser
import os

from common import fetch_page

# Google's preferences pages
URL = 'https://www.google.com/preferences'
CACHEPATH = os.path.join(os.path.dirname(__file__), 'google.html')


def parse_page(html):
    """Parse language id-name pairs from HTML.

    Args:
        html (unicode): Google's preferences page.

    Returns:
        list: Sequence of 2-tuples: `(id, name)`.
    """
    langs = []
    parser = HTMLParser()

    while True:
        i = html.find('<option value=')
        if i < 0:
            break
        html = html[i+len('<option value='):]
        i = html.find('>')
        key = html[:i]
        if key.endswith(' selected'):
            key = key[:-len(' selected')]
        html = html[i+1:]
        i = html.find(' <')
        name = parser.unescape(html[:i])
        html = html[i+1:]
        if key.startswith('xx-'):  # Novelty language, like xx-bork
            continue
        if key[0] not in 'abcdefghijklmnopqrstuvwxyz':
            continue

        langs.append((key, name))

    return langs


def main():
    """Parse and print languages from Google's preferences page."""
    html = fetch_page(URL, CACHEPATH).decode('ISO-8859-1')
    langs = parse_page(html)
    for key, name in sorted(langs):
        print('{}\t{}'.format(key, name).encode('utf-8'))

if __name__ == '__main__':
    main()
