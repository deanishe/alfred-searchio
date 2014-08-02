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
    search.py [-t|--text] (-L|--list)

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
from urllib import quote_plus
import subprocess

from workflow import Workflow, web, ICON_ERROR


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

    def __init__(self, wf, options):
        self.wf = wf
        self.options = options
        # Map language to region for engines that require that
        if self.options['lang'] in self._lang_region_map:
            self.options['lang'] = self._lang_region_map[self.options['lang']]

    def search(self):
        components = [self.name]
        for t in self.options.items():
            components.extend(t)
        m = md5()
        log.debug(components)
        m.update(':'.join(components).encode('utf-8'))
        key = m.hexdigest()
        return self.wf.cached_data(key, self._suggest, max_age=600)
        # Add query to results
        # results = self.wf.cached_data(key, self._suggest, max_age=600)
        # return [self.options['query']] + results

    def _suggest(self):
        """Return list of unicode suggestions"""
        raise NotImplementedError()

    def url_for(self, query):
        """Return browser URL for `query`"""
        url = self.search_url.encode('utf-8')
        options = self.options.copy()
        options['query'] = query
        for key in options:
            options[key] = quote_plus(options[key].encode('utf-8'))
        return url.format(**options)


class Google(Suggest):
    """Get search suggestions from Google"""

    id_ = 'google'
    name = 'Google'
    _suggest_url = 'https://suggestqueries.google.com/complete/search'
    _search_url = 'http://www.google.com/webhp?q={query}#hl={lang}&safe=off&q={query}'

    def _suggest(self):
        response = web.get(self.suggest_url, {'client': 'firefox',
                                              'q': self.options['query'],
                                              'hl': self.options['lang']})
        response.raise_for_status()
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
        if display_text:
            length = sorted([len(l) for l in engines.keys()])[-1]
            fmt = '{{:{}s}} | {{}}'.format(length)
            print('Supported search engines\n')
            print('Use `-e ENGINE_ID` to specify the search engine.\n')
            print(fmt.format('ID', 'Search Engine'))
            print('-' * 40)
            for id_ in sorted(engines):
                print(fmt.format(id_, engines[id_].name))
            print()
        else:
            name_id_list = sorted([(cls.name, id_, cls) for (id_, cls) in
                                   engines.items()])
            for name, id_, cls in name_id_list:
                wf.add_item(
                    name,
                    'Use `--engine {}` in your Script Filter'.format(id_),
                    valid=False,
                    icon='icons/{}.png'.format(cls.id_))
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
    engine = engines[options['engine']](wf, options)

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
