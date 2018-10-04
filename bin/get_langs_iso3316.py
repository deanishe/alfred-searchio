#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-13
#

"""Output TSV list of ISO-639-1 language ``code,name``."""

from __future__ import print_function, absolute_import

from common import datapath, httpget, Lang, print_lang

from bs4 import BeautifulSoup as BS


url = 'https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes'
cachepath = datapath('ISO 3316-1 Country Codes.html')


def main():
    html = httpget(url, cachepath)
    soup = BS(html, 'html.parser')
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) != 10:
            continue
        cells = cells[3:5]
        # print(cells)
        name, abbr = [e.get_text().strip() for e in cells]
        if len(abbr) != 2:
            continue

        name = name.split(u',', 1)[0].strip()

        print_lang(Lang(abbr, name))


if __name__ == '__main__':
    main()
