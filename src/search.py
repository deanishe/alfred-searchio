#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-05-11
#

"""All auto-completion engines rolled into one script.

Note: This script is currently not in use in the workflow.

To use, create a Script Filter with the following bash script:

    /usr/bin/python search.py engine_id "{query}"

where `engine_id` corresponds to the `id_` attribute of one of the
`Suggest` subclasses below.

"""

from __future__ import print_function, unicode_literals

import sys
from hashlib import md5
from urllib import quote_plus

from workflow import Workflow, web, ICON_ERROR


log = None


class Suggest(object):
    """Base class for auto-suggestion

    Subclasses must override ``name``, ``icon``,
    ``suggest_url`` and ``search_url`` class attributes,
    and ``_suggest`` method.

    ``url_for`` method may also need to be overridden.

    """

    name = None
    icon = None
    suggest_url = None
    search_url = None

    def __init__(self, wf):
        self.wf = wf
        self.query = None

    def search(self, query):
        self.query = query
        m = md5()
        m.update('{}-{}'.format(self.name, query).encode('utf-8'))
        key = m.hexdigest()
        return self.wf.cached_data(key, self._suggest, max_age=600)

    def _suggest(self):
        """Return list of unicode suggestions"""
        raise NotImplementedError()

    def url_for(self, query):
        """Return browser URL for `query`"""
        url = self.search_url.encode('utf-8')
        return url.format(query=quote_plus(query.encode('utf-8')))


class Google(Suggest):

    id_ = 'google'
    name = 'Google'
    icon = 'google.png'
    suggest_url = 'https://suggestqueries.google.com/complete/search'
    search_url = 'http://www.google.com/webhp?q={query}#hl=en&safe=off&q={query}'

    def _suggest(self):
        response = web.get(self.suggest_url, {'client': 'firefox',
                                              'q': self.query})
        response.raise_for_status()
        _, results = response.json()
        return results


class Bing(Suggest):

    id_ = 'bing'
    name = 'Bing'
    icon = 'bing.png'
    suggest_url = 'http://api.bing.com/osjson.aspx'
    search_url = 'https://www.bing.com/search?q={query}&go=Submit&qs=n&form=QBRE&filt=all&pq={query}&sc=8-6&sp=-1&sk='

    def _suggest(self):
        response = web.get(self.suggest_url, {'query': self.query})
        response.raise_for_status()
        _, results = response.json()
        return results


class DuckDuckGo(Suggest):

    id_ = 'ddg'
    name = 'DuckDuckGo'
    icon = 'ddg.png'
    suggest_url = 'https://duckduckgo.com/ac/'
    search_url = 'https://duckduckgo.com/?q={query}'

    def _suggest(self):
        response = web.get(self.suggest_url, {'q': self.query})
        response.raise_for_status()
        results = response.json()
        return [d.get('phrase') for d in results]


class Wiktionary(Suggest):

    id_ = 'wiktionary'
    name = 'Wiktionary'
    icon = 'wiktionary.png'
    suggest_url = 'https://en.wiktionary.org/w/api.php'
    search_url = 'https://en.wiktionary.org/wiki/{query}'

    def _suggest(self):
        response = web.get(self.suggest_url, {'action': 'opensearch',
                                              'search': self.query})
        response.raise_for_status()
        _, results = response.json()
        return results


class WikipediaEnglish(Suggest):

    id_ = 'wikipedia_en'
    name = 'Wikipedia (English)'
    icon = 'wikipedia.png'
    suggest_url = 'https://en.wikipedia.org/w/api.php'
    search_url = 'https://en.wikipedia.org/wiki/{query}'

    def _suggest(self):
        response = web.get(self.suggest_url, {'action': 'opensearch',
                                              'search': self.query})
        response.raise_for_status()
        _, results = response.json()
        return results


class WikipediaGerman(Suggest):

    id_ = 'wikipedia_de'
    name = 'Wikipedia (German)'
    icon = 'wikipedia.png'
    suggest_url = 'https://de.wikipedia.org/w/api.php'
    search_url = 'https://de.wikipedia.org/wiki/{query}'

    def _suggest(self):
        response = web.get(self.suggest_url, {'action': 'opensearch',
                                              'search': self.query})
        response.raise_for_status()
        _, results = response.json()
        return results


def main(wf):
    engine_id, query = wf.args[:2]
    engines = {}
    for cls in Suggest.__subclasses__():
        log.debug('subclass : {}'.format(cls.name))
        engines[cls.id_] = cls

    if engine_id not in engines:
        wf.add_item('Invalid engine: {}',
                    'Check your workflow settings',
                    icon=ICON_ERROR)
        wf.send_feedback()
        return

    # Instantiate `Suggest` subclass with workflow object
    engine = engines[engine_id](wf)

    results = engine.search(query)

    if not results:
        wf.add_item("Search {} for '{}'".format(engine.name, query),
                    valid=True,
                    arg=engine.url_for(query),
                    icon=engine.icon)

    else:
        for phrase in results:
            url = engine.url_for(phrase)
            wf.add_item(phrase,
                        valid=True,
                        uid=url,
                        arg=url,
                        icon=engine.icon)

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
