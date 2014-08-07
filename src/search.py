#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-05-11
#

"""search.py [options] [<query>]

Provide auto-suggestion results for <query>

Usage:
    search.py [(-t|--text)] [-e|--engine ENGINE_ID] [--lang LANG] [<query>]
    search.py (-h|--help)
    search.py [-t|--text] (-L|--list) [<query>]

Options:
    -e, --engine=ENGINE_ID  ID of search engine to use
    -l, --lang=LANG         2-letter language (default is system language)
    -t, --text              Print results as text, not Alfred XML
    -L, --list              List supported search engines
    -h, --help              Display this help message

"""

from __future__ import print_function, unicode_literals

import sys
from hashlib import md5
import urllib
import subprocess

from workflow import Workflow, web, ICON_ERROR, ICON_SETTINGS


DEFAULT_ENGINE = 'google'


log = None


def get_system_language():
    """Return system language"""
    output = subprocess.check_output(['defaults', 'read', '-g',
                                      'AppleLanguages'])
    output = output.strip('()\n ')
    langs = [s.strip('", ') for s in output.split('\n')]
    if not len(langs):
        raise ValueError('Could not determine system language')
    lang = langs[0]
    if len(lang) > 2:
        lang = lang[:2]
    return lang


class Suggest(object):
    """Base class for auto-suggestion

    Subclasses must override ``name``, ``icon``,
    ``suggest_url`` and ``search_url`` class attributes,
    and ``_suggest`` method.

    ``url_for`` method may also need to be overridden.

    """

    id_ = None
    name = None
    _suggest_url = None
    _search_url = None
    _custom_suggest_urls = {}
    _custom_search_urls = {}
    _lang_region_map = {}
    _quote_plus = True

    def __init__(self, wf, options, show_query_in_results=False):
        self.wf = wf
        self.options = options
        self.show_query_in_results = show_query_in_results
        # Map language to region for engines that require that
        if self.options['lang'] in self._lang_region_map:
            self.options['lang'] = self._lang_region_map[self.options['lang']]

    @property
    def icon(self):
        return 'icons/{}.png'.format(self.id_)

    @property
    def suggest_url(self):
        url = self._custom_suggest_urls.get(self.options['lang'],
                                            self._suggest_url)
        return url.format(**self.options)

    @property
    def search_url(self):
        url = self._custom_search_urls.get(self.options['lang'],
                                           self._search_url)
        # Ensure {query} is not added from options (it'll be added by `url_for`)
        url = url.replace('{query}', '{{query}}')
        return url.format(**self.options)

    def search(self):
        # Create cache key
        components = [self.name]
        for t in self.options.items():
            components.extend(t)
        m = md5()
        log.debug('key components : {}'.format(components))
        m.update(':'.join(components).encode('utf-8'))
        key = m.hexdigest()

        # return self.wf.cached_data(key, self._suggest, max_age=600)
        results = self.wf.cached_data(key, self._suggest, max_age=600)

        # Add query to results
        if self.show_query_in_results:
            results = [self.options['query']] + results

        return results

    def _suggest(self):
        """Return list of unicode suggestions"""
        raise NotImplementedError()

    def url_for(self, query):
        """Return browser URL for `query`"""
        url = self.search_url.encode('utf-8')
        options = self.options.copy()
        options['query'] = query
        for key in options:
            if self._quote_plus:
                options[key] = urllib.quote_plus(options[key].encode('utf-8'))
            else:
                options[key] = urllib.quote(options[key].encode('utf-8'))
        return url.format(**options)


class Google(Suggest):
    """Get search suggestions from Google"""

    id_ = 'google'
    name = 'Google'
    _suggest_url = 'https://suggestqueries.google.com/complete/search'
    _search_url = 'https://www.google.com/search?q={query}&hl={lang}&safe=off'

    def _suggest(self):
        response = web.get(self.suggest_url, {'client': 'firefox',
                                              'q': self.options['query'],
                                              'hl': self.options['lang']})
        response.raise_for_status()
        _, results = response.json()
        return results


class GoogleImages(Suggest):
    """Get search suggestions from Google Images"""

    id_ = 'google-images'
    name = 'Google Images'
    _suggest_url = 'https://suggestqueries.google.com/complete/search'
    _search_url = 'https://www.google.com/search?tbm=isch&q={query}&hl={lang}&safe=off'
    # _search_url = 'https://www.google.com/search?q={query}&hl={lang}&safe=off'

    def _suggest(self):
        response = web.get(self.suggest_url, {'client': 'firefox',
                                              'ds': 'i',
                                              'q': self.options['query'],
                                              'hl': self.options['lang']})
        response.raise_for_status()
        _, results = response.json()
        return results


class GoogleMaps(Suggest):
    """Get search suggestions from Google Maps"""

    id_ = 'google-maps'
    name = 'Google Maps'
    _suggest_url = 'https://maps.google.com/maps/suggest'
    _search_url = 'https://www.google.com/search?q={query}&hl={lang}&safe=off'

    def _suggest(self):
        response = web.get(self.suggest_url, {'v': '2',
                                              'cp': '999',
                                              'json': 'b',
                                              'q': self.options['query'],
                                              'hl': self.options['lang'],
                                              'gl': self.options['lang']})
        response.raise_for_status()

        results = response.json().get('suggestion', [])

        if not results:
            return []
        results = [d['query'] for d in results if 'query' in d]

        return results


class YouTube(Suggest):
    """Get search suggestions from Youtube"""

    id_ = 'youtube'
    name = 'YouTube'
    _suggest_url = 'https://suggestqueries.google.com/complete/search'
    _search_url = 'https://www.youtube.com/results?search_query={query}'
    # _search_url = 'https://www.google.com/search?q={query}&hl={lang}&safe=off'

    def _suggest(self):
        response = web.get(self.suggest_url, {'client': 'firefox',
                                              'ds': 'yt',
                                              'q': self.options['query'],
                                              'hl': self.options['lang']})
        response.raise_for_status()
        _, results = response.json()
        return results


class Amazon(Suggest):
    """Get search suggestions from Amazon"""

    # markets
    # 1 = us
    # 2 = ??
    # 3 = uk
    # 4 = de
    # 5 = fr
    # 7 = ca
    # 44551 = es

    id_ = 'amazon'
    name = 'Amazon'
    _suggest_url = 'https://completion.amazon.com/search/complete'
    _search_url = 'https://www.amazon.{lang}/gp/search?ie=UTF8&keywords={query}'
    _lang_region_map = {
        'en': 'com',
        'uk': 'co.uk',
        'de': 'de',
        'fr': 'fr',
        'ca': 'ca',
        'es': 'es',
    }
    _custom_suggest_urls = {
        'co.uk': 'https://completion.amazon.co.uk/search/complete',
        'de': 'https://completion.amazon.co.uk/search/complete',
        'fr': 'https://completion.amazon.co.uk/search/complete',
        'es': 'https://completion.amazon.co.uk/search/complete',
    }

    _domain_market_map = {
        'com': '1',
        'co.uk': '3',
        'de': '4',
        'fr': '5',
        'ca': '7',
        'es': '44551',
    }

    def _suggest(self):
        market = self._domain_market_map.get(self.options['lang'], '1')
        response = web.get(self.suggest_url, {'method': 'completion',
                                              'search-alias': 'aps',
                                              'q': self.options['query'],
                                              'mkt': market})
        response.raise_for_status()
        results = response.json()[1]
        return results


class Ebay(Suggest):
    """Get search suggestions from eBay"""

    id_ = 'ebay'
    name = 'eBay'
    _suggest_url = 'https://anywhere.ebay.com/services/suggest/'
    _search_url = 'http://shop.ebay.{lang}/?_nkw={query}'
    _lang_region_map = {
        'en': 'com',
        'uk': 'co.uk',
    }

    def _suggest(self):
        response = web.get(self.suggest_url, {'s': '0',
                                              'q': self.options['query']})
        response.raise_for_status()
        log.debug(response.url)
        _, results = response.json()
        return results


class Bing(Suggest):
    """Get search suggestions from Bing

    Bing has specific Market (i.e. region) settings plus a ``language:``

    argument in the search query.

    TODO: Implement markets as well as/instead of language
    """

    id_ = 'bing'
    name = 'Bing'
    _suggest_url = 'http://api.bing.com/osjson.aspx'
    _search_url = 'https://www.bing.com/search?q={query}&go=Submit&qs=n&form=QBRE&filt=all&pq={query}&sc=8-6&sp=-1&sk='

    def _suggest(self):
        response = web.get(self.suggest_url, {'query': self.options['query'],
                                              'language': self.options['lang']})
        response.raise_for_status()
        _, results = response.json()
        return results

    def url_for(self, query):
        query = query + ' language:{}'.format(self.options['lang'])
        return super(Bing, self).url_for(query)


class Yahoo(Suggest):
    """Get search suggestions from Yahoo!"""

    id_ = 'yahoo'
    name = 'Yahoo!'
    _suggest_url = 'http://{lang}-sayt.ff.search.yahoo.com/gossip-{lang}-sayt'
    _search_url = 'https://{lang}.search.yahoo.com/search?ei=utf-8&fr=crmas&p={query}'
    _custom_suggest_urls = {
        'en': 'http://ff.search.yahoo.com/gossip'
    }
    _custom_search_urls = {
        'en': 'https://search.yahoo.com/search?ei=utf-8&fr=crmas&p={query}'
    }

    def _suggest(self):
        url = self.suggest_url.format(lang=self.options['lang'])
        response = web.get(url, {'output': 'fxjson', 'command': self.options['query']})
        response.raise_for_status()
        results = response.json()[1]
        return results


class DuckDuckGo(Suggest):
    """Get search suggestions from DuckDuckGo

    DDG does not provide language-specific suggestions, as far as I can tell.
    """

    id_ = 'ddg'
    name = 'DuckDuckGo'
    _suggest_url = 'https://duckduckgo.com/ac/'
    _search_url = 'https://duckduckgo.com/?q={query}'
    _lang_region_map = {
        'en': 'us'
    }

    def _suggest(self):
        response = web.get(self.suggest_url, {'q': self.options['query']})
        response.raise_for_status()
        results = response.json()
        return [d.get('phrase') for d in results]

    def url_for(self, query):
        query = query + ' r:{}'.format(self.options['lang'])
        url = super(DuckDuckGo, self).url_for(query)
        log.debug(url)
        return url


class Wiktionary(Suggest):
    """Get search suggestions from Wiktionary"""

    id_ = 'wiktionary'
    name = 'Wiktionary'
    _suggest_url = 'https://{lang}.wiktionary.org/w/api.php'
    _search_url = 'https://{lang}.wiktionary.org/wiki/{query}'
    _quote_plus = False

    def _suggest(self):
        url = self.suggest_url.format(lang=self.options['lang'])
        response = web.get(url, {'action': 'opensearch',
                                 'search': self.options['query']})
        response.raise_for_status()
        _, results = response.json()
        return results


class Wikipedia(Suggest):
    """Get search suggestions from Wikipedia"""

    id_ = 'wikipedia'
    name = 'Wikipedia'
    _suggest_url = 'https://{lang}.wikipedia.org/w/api.php'
    _search_url = 'https://{lang}.wikipedia.org/wiki/{query}'
    _quote_plus = False

    def _suggest(self):
        url = self.suggest_url.format(lang=self.options['lang'])
        response = web.get(url, {'action': 'opensearch',
                                 'search': self.options['query']})
        response.raise_for_status()
        _, results = response.json()
        return results


class Ask(Suggest):
    """Get search suggestions from Ask.com"""

    id_ = 'ask'
    name = 'Ask'
    _suggest_url = 'http://ss.{lang}.ask.com/query'
    _search_url = 'http://{lang}.ask.com/web?q={query}'
    _custom_suggest_urls = {
        'en': 'http://ss.ask.com/query'
    }
    _custom_search_urls = {
        'en': 'http://ask.com/web?q={query}'
    }

    def _suggest(self):
        response = web.get(self.suggest_url,
                           {'li': 'ff', 'q': self.options['query']})
        response.raise_for_status()
        _, results = response.json()
        return results


def main(wf):
    from docopt import docopt

    args = docopt(__doc__, wf.args)

    display_text = args.get('--text')
    del(args['--text'])

    engines = {}
    for cls in Suggest.__subclasses__():
        log.debug('subclass : {}'.format(cls.name))
        engines[cls.id_] = cls

    ####################################################################
    # List engines
    ####################################################################

    if args.get('--list'):  # Show list of supported engines

        query = args.get('<query>')

        name_id_list = sorted([(cls.name, id_) for (id_, cls) in
                               engines.items()])

        if query:
            name_id_list = wf.filter(query, name_id_list, lambda x: x[0])

        if display_text:  # Display for terminal
            length = sorted([len(t[1]) for t in name_id_list])[-1]
            fmt = '{{:{}s}} | {{}}'.format(length)
            print('Supported search engines\n')
            print('Use `-e ENGINE_ID` to specify the search engine.\n')
            print(fmt.format('ENGINE_ID', 'Search Engine'))
            print('-' * 40)
            for name, id_ in name_id_list:
                print(fmt.format(id_, name))
            print()

        else:  # Display for Alfred
            # Show settings
            qir = ('No', 'Yes')[wf.settings.get('show_query_in_results', False)]
            wf.add_item('Show query in results: {}'.format(qir),
                        'Action this item to toggle setting',
                        arg='show_query_in_results',
                        valid=True,
                        icon=ICON_SETTINGS)

            for name, id_ in name_id_list:
                wf.add_item(
                    name,
                    'Use `--engine {}` in your Script Filter'.format(id_),
                    valid=False,
                    icon='icons/{}.png'.format(id_))
            wf.send_feedback()
        return

    ####################################################################
    # Perform search and show results
    ####################################################################

    # Turn args into proper dictionary of options
    options = {}
    for arg, value in args.items():
        if arg in ('--list', '--help'):  # Script options
            continue
        if arg.startswith('<') and arg.endswith('>'):
            options[arg[1:-1]] = value
        elif arg.startswith('--'):
            options[arg[2:]] = value

    if not options.get('lang'):
        options['lang'] = wf.cached_data('default-language',
                                         get_system_language,
                                         max_age=3600)

    if not options.get('engine'):
        options['engine'] = DEFAULT_ENGINE

    if not options['engine'] in engines:
        if display_text:
            print("Unknown engine : '{}'. Use `--list` to see "
                  "valid engines.".format(options['engine']),
                  file=sys.stderr)
            sys.exit(1)
        else:
            wf.add_item('Invalid engine: {}'.format(options['engine']),
                        'Check your workflow settings',
                        icon=ICON_ERROR)
            wf.send_feedback()
            return

    # Instantiate `Suggest` subclass with workflow object
    engine = engines[options['engine']](wf, options,
                                        wf.settings.get('show_query_in_results',
                                                        False))

    results = engine.search()

    if not results:
        if display_text:
            print('No results', file=sys.stderr)
        else:
            wf.add_item(
                "Search {} for '{}'".format(engine.name, options['query']),
                valid=True,
                arg=engine.url_for(options['query']),
                icon=engine.icon)

    else:
        if display_text:
            length = sorted([len(r) for r in results])[-1]
            fmt = '{{:{}s}} {{}}'.format(length)
            for phrase in results:
                print(fmt.format(phrase, engine.url_for(phrase)))
        else:
            for phrase in results:
                url = engine.url_for(phrase)
                wf.add_item(phrase,
                            "Search {} for '{}'".format(engine.name, phrase),
                            valid=True,
                            uid=url,
                            arg=url,
                            icon=engine.icon)

    if not display_text:
        wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
