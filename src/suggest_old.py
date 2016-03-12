class Suggest(object):
    """Base class for auto-suggestion.

    Subclasses must override `id_`, `name`,
    `_suggest_url` and `_search_url` class attributes,
    and `_suggest` method.

    `url_for` method may also need to be overridden.

    Attributes:
        id_ (str): Program name of the engine. Used on command line.
            E.g. 'google-images'.
        name (str): Human-readable name of engine, e.g. 'Google Images'.
        options (dict): Search parameters, most importantly `query`.
        show_query_in_results (bool): Add query to start of results.
        wf (workflow.Workflow): Active `Workflow` object.
    """

    id_ = None
    name = None
    #: Base URL for suggestions (with formatting placeholders)
    _suggest_url = None
    #: Base URL for searches  (with formatting placeholders)
    _search_url = None
    #: Mapping of `lang` to custom URLs
    _custom_suggest_urls = {}
    #: Mapping of `lang` to custom URLs
    _custom_search_urls = {}
    #: Mapping of `lang` (or region) to TLDs, e.g. `'uk': 'co.uk'`
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
        """Relative path to icon for Alfred results."""
        return 'icons/{0}.png'.format(self.id_)

    @property
    def suggest_url(self):
        """URL to fetch suggestions from."""
        url = self._custom_suggest_urls.get(self.options['lang'],
                                            self._suggest_url)
        return url.format(**self.options)

    @property
    def search_url(self):
        """URL for full search results (webpage)."""
        url = self._custom_search_urls.get(self.options['lang'],
                                           self._search_url)
        # Ensure {query} is not added from options (it'll be added by `url_for`)
        url = url.replace('{query}', '{{query}}')
        return url.format(**self.options)

    def search(self):
        """Call `_suggest()` subclass method, and cache and return suggestions.

        Returns:
            list: Unicode search suggestions.
        """
        # Create cache key
        components = [self.name]
        for t in self.options.items():
            components.extend(t)
        m = md5()
        log.debug('key components : {0}'.format(components))
        m.update(':'.join(components).encode('utf-8'))
        key = m.hexdigest()

        # return self.wf.cached_data(key, self._suggest, max_age=600)
        results = self.wf.cached_data(key, self._suggest, max_age=600)

        # Add query to results
        if self.show_query_in_results:
            results = [self.options['query']] + results

        return results

    def _suggest(self):
        """Return list of unicode suggestions."""
        raise NotImplementedError()

    def url_for(self, query):
        """Return browser URL for `query`."""
        url = self.search_url.encode('utf-8')
        options = self.options.copy()
        options['query'] = query
        for key in options:
            if self._quote_plus:
                options[key] = urllib.quote_plus(options[key].encode('utf-8'))
            else:
                options[key] = urllib.quote(options[key].encode('utf-8'))
        return url.format(**options)


class Yandex(Suggest):
    """Get search suggestions from Yandex.ru."""

    id_ = 'yandex'
    name = 'Yandex.ru'
    _suggest_url = 'http://suggest.yandex.net/suggest-ff.cgi'
    _search_url = 'http://yandex.ru/yandsearch?text={query}'

    def _suggest(self):
        response = web.get(self.suggest_url, {'part': self.options['query']})
        response.raise_for_status()
        _, results = response.json()
        return results


class Naver(Suggest):
    """Get search suggestions from Naver.com"""

    id_ = 'naver'
    name = 'Naver.com'
    _suggest_url = 'http://ac.search.naver.com/nx/ac'
    _search_url = 'http://search.naver.com/search.naver?ie=utf-8&query={query}'

    def _suggest(self):
        response = web.get(self.suggest_url, {
                           'q': self.options['query'],
                           'of': 'os',
                           'ie': 'utf-8',
                           'oe': 'utf-8',
                           })
        response.raise_for_status()
        results = response.json()[1]
        return results


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
    _search_url = ('https://www.google.com/search?tbm=isch&'
                   'q={query}&hl={lang}&safe=off')
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
    _search_url = 'https://www.google.com/maps/preview?q={query}&hl={lang}'

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
    # 526970 = com.br

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
        'pt': 'com.br',
    }
    _custom_suggest_urls = {
        'co.uk': 'https://completion.amazon.co.uk/search/complete',
        'de': 'https://completion.amazon.co.uk/search/complete',
        'fr': 'https://completion.amazon.co.uk/search/complete',
        'es': 'https://completion.amazon.co.uk/search/complete',
        'com.br': 'https://completion.amazon.com/search/complete',
    }

    _domain_market_map = {
        'com': '1',
        'co.uk': '3',
        'de': '4',
        'fr': '5',
        'ca': '7',
        'es': '44551',
        'com.br': '526970',
    }

    def _suggest(self):
        market = self._domain_market_map.get(self.options['lang'], '1')
        response = web.get(self.suggest_url, {'method': 'completion',
                                              'search-alias': 'aps',
                                              'client': 'alfred-searchio',
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

    Bing has specific Market (i.e. region) settings plus a `language:`

    argument in the search query.

    TODO: Implement markets as well as/instead of language
    """

    id_ = 'bing'
    name = 'Bing'
    _suggest_url = 'http://api.bing.com/osjson.aspx'
    _search_url = ('https://www.bing.com/search?q={query}&go=Submit&'
                   'qs=n&form=QBRE&filt=all&pq={query}&sc=8-6&sp=-1&sk=')

    def _suggest(self):
        response = web.get(self.suggest_url,
                           {'query': self.options['query'],
                            'language': self.options['lang']})
        response.raise_for_status()
        _, results = response.json()
        return results

    def url_for(self, query):
        query = query + ' language:{0}'.format(self.options['lang'])
        return super(Bing, self).url_for(query)


class Yahoo(Suggest):
    """Get search suggestions from Yahoo!"""

    id_ = 'yahoo'
    name = 'Yahoo!'
    _suggest_url = 'http://{lang}-sayt.ff.search.yahoo.com/gossip-{lang}-sayt'
    _search_url = ('https://{lang}.search.yahoo.com/search?ei=utf-8&'
                   'fr=crmas&p={query}')
    _custom_suggest_urls = {
        'en': 'http://ff.search.yahoo.com/gossip'
    }
    _custom_search_urls = {
        'en': 'https://search.yahoo.com/search?ei=utf-8&fr=crmas&p={query}'
    }

    def _suggest(self):
        url = self.suggest_url.format(lang=self.options['lang'])
        response = web.get(url, {'output': 'fxjson',
                                 'command': self.options['query']})
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
        query = query + ' r:{0}'.format(self.options['lang'])
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
        _, results = response.json()[0:2]
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
        _, results = response.json()[0:2]
        return results


class Wikia(Suggest):
    """Get search suggestions from Wikia"""

    id_ = 'wikia'
    name = 'Wikia'
    _suggest_url = 'https://{lang}.wikia.com/api.php'
    _search_url = 'https://{lang}.wikia.com/wiki/{query}'
    _quote_plus = False

    def _suggest(self):
        url = self.suggest_url.format(lang=self.options['lang'])
        response = web.get(url, {'action': 'opensearch',
                                 'search': self.options['query']})
        response.raise_for_status()
        _, results = response.json()[0:2]
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

