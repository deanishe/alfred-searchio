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
"""

from __future__ import print_function, unicode_literals, absolute_import

from urllib import urlopen

from bs4 import BeautifulSoup as BS


url = 'https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes'


def main():
    html = urlopen(url).read().decode('utf-8')
    soup = BS(html)
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) != 10:
            continue
        cells = cells[3:5]
        # print(cells)
        name, abbr = [e.get_text().strip() for e in cells]
        if len(abbr) != 2:
            continue

        name = name.split(',', 1)[0].strip()

        print('{0}\t{1}'.format(abbr, name).encode('utf-8'))


if __name__ == '__main__':
    main()
