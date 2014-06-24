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
Get autocomplete results for query from Bing.com
"""

from __future__ import print_function, unicode_literals

from workflow import Workflow, web

SEARCH_URL = 'http://api.bing.com/osjson.aspx'


def main(wf):
    query = wf.args[0]
    response = web.get(SEARCH_URL, {'query': query})
    wf.logger.debug('URL : {}'.format(response.url))
    response.raise_for_status()
    _, results = response.json()

    if not results:
        wf.add_item("Search Bing for '{}'".format(query),
                    '',
                    valid=True,
                    arg=query,
                    icon='bing.png')

    for phrase in results:
        wf.add_item(phrase, 'Search web',
                    valid=True,
                    arg=phrase,
                    uid=phrase,
                    icon='bing.png')
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)
