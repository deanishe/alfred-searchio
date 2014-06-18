#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-05-11
#

"""
Get autocomplete results for query from DuckDuckGo.com
"""

from __future__ import print_function, unicode_literals

from workflow import Workflow, web

SEARCH_URL = 'https://duckduckgo.com/ac/'


def main(wf):
    query = wf.args[0]
    response = web.get(SEARCH_URL, {'q': query})
    wf.logger.debug('URL : {}'.format(response.url))
    response.raise_for_status()
    results = response.json()

    if not results:
        wf.add_item("Search DuckDuckGo for '{}'".format(query),
                    '',
                    arg=query,
                    icon='ddg.png')

    for d in results:
        phrase = d['phrase']
        wf.add_item(phrase, 'Search web',
                    valid=True,
                    arg=phrase,
                    uid=phrase,
                    icon='ddg.png')
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)
