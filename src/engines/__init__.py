#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-01
#

"""
Searchio! search engines.
"""

from __future__ import print_function, unicode_literals, absolute_import

import abc
from hashlib import md5
import logging
import os
import urllib

from workflow import web

log = logging.getLogger('workflow.{0}'.format(__name__))

imported_dirs = set()

# TODO: Create plugin objects from JSON files.

def url_encode_dict(dic):
    """Copy of `dic` with values URL-encoded.

    Leave keys unaltered, URL-encode values (i.e. UTF-8 strings).

    Args:
        dic (TYPE): Dictionary whose values to URL-encode.

    Returns:
        dict: New dictionary with URL-encoded values.
    """
    encoded = {}

    for k, v in dic.items():
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        elif not isinstance(v, str):
            v = str(v)
        encoded[k] = urllib.quote_plus(v)

    return encoded


class SuggestBase(object):
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

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def id(self):
        """Short name of the engine, used on the command line.

        E.g., 'amazon' or 'google-images'.
        """
        return

    @abc.abstractproperty
    def name(self):
        """Human-readable name of engine.

        E.g., 'Amazon' or 'Google Images'.
        """
        return

    @abc.abstractproperty
    def suggest_url(self):
        """Default base URL for suggestions (with formatting placeholders)."""
        return

    @abc.abstractproperty
    def search_url(self):
        """Default base URL for searches (with formatting placeholders)."""
        return

    @abc.abstractproperty
    def variants(self):
        """Return a `dict` of search engine language/region variants.

        E.g.:
            'uk': {
                'name': 'United Kingdom',
                'suggest_url': 'https://uk.example.com/ac',
                'search_url': 'https://uk.example.com/search'
            },
            ...

        Only name is required.
        """
        return

    def suggest(self, query, variant_id):
        """Return list of unicode suggestions."""
        url = self.get_suggest_url(query, variant_id)
        r = web.get(url)
        log.debug('[%s] %s', r.status_code, r.url)
        r.raise_for_status()
        return self._post_process_response(r.json())

    def _post_process_response(self, response_data):
        _, results = response_data
        return results

    @property
    def icon(self):
        """Relative path to icon for Alfred results.

        Assumes icon is in same directory as this Python module and is
        called `<id>.png` where `<id>` is the `id` of the class.
        """
        filename = '{0}.png'.format(self.id)
        return os.path.join(os.path.dirname(__file__), filename)

    def get_suggest_url(self, query, variant_id):
        """URL to fetch suggestions from."""
        if variant_id not in self.variants:
            raise ValueError('Unknown variant : {0!r}'.format(variant_id))

        variant = self.variants[variant_id]

        # TODO: Apply variables to URLs
        rplc = dict(query=query, variant=variant_id)
        rplc.update(variant.get('vars', {}))

        rplc = url_encode_dict(rplc)

        url = variant.get('suggest_url', self.suggest_url)
        return url.format(**rplc)

    def get_search_url(self, query, variant_id):
        """URL for full search results (webpage)."""
        if variant_id not in self.variants:
            raise ValueError('Unknown variant : {0!r}'.format(variant_id))
        # TODO: Add GET var replacement/addition?
        variant = self.variants[variant_id]
        rplc = {'query': query, 'variant': variant_id}
        rplc.update(variant.get('vars', {}))
        rplc = url_encode_dict(rplc)

        url = variant.get('search_url', self.search_url)
        return url.format(**rplc)
        # return self.variants[variant].get('search_url', self.search_url)
        # url = self._custom_search_urls.get(self.options['lang'],
        #                                    self.default_search_url)
        # Ensure {query} is not added from options (it'll be added by `url_for`)
        # url = url.replace('{query}', '{{query}}')
        # return url.format(**self.options)

    # def suggest(self, query, variant):
    #     """Cache and return suggestions from `_suggest()` method on subclasses.

    #     Returns:
    #         list: Unicode search suggestions.
    #     """
    #     # Create cache key
    #     key = '{0}/{1}/{2}'.format(self.id, variant,
    #                                md5(query.encode('utf-8')).hexdigest())
    #     # for t in self.options.items():
    #     #     components.extend(t)
    #     # key = md5(':'.join(components).encode('utf-8')).hexdigest()
    #     # log.debug('key components : {0!r}'.format(components))

    #     def _wrapper():
    #         return self._suggest(query, variant)

    #     results = self.wf.cached_data(key, self._wrapper, max_age=600)

    #     # Add query to results
    #     if self.show_query_in_results:
    #         results = [self.options['query']] + results

    #     return results

    def search(self, query, variant):
        """Synonym for `suggest()`."""
        return self.suggest(query, variant)

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


def _get_engine_modules(dirpath):
    """Return list of files in dirpath matching `*.py`"""

    modnames = []

    for filename in os.listdir(dirpath):
        if filename.endswith('.py') and not filename.startswith('_'):
            name = os.path.splitext(filename)[0]
            modnames.append(name)

    return modnames


def import_engines(dirpath):
    """Import all `*.py` modules within directory `dirpath`.

    Modules will be imported under `engines.user_<modname>`.

    As a result, user modules may override built-ins.

    """

    dirpath = os.path.abspath(dirpath)

    if dirpath in imported_dirs:
        log.debug('Directory already imported : `%s`', dirpath)
        return

    imported_dirs.add(dirpath)

    # Is `dirpath` this package?
    builtin = dirpath == os.path.abspath(os.path.dirname(__file__))

    if not builtin and dirpath not in sys.path:
        sys.path.append(dirpath)

    kind = ('user', 'built-in')[builtin]

    for modname in _get_engine_modules(dirpath):
        if builtin:
            modname = 'engines.{0}'.format(modname)

        try:
            __import__(modname)
            log.debug('Imported %s generators from `%s`', kind, modname)
        except Exception as err:
            log.error('Error importing `%s` : %s', modname, err)


def get_subclasses(klass):
    """Return list of all subclasses of `klass`.

    Also recurses into subclasses.

    """

    subclasses = []

    for cls in klass.__subclasses__():
        subclasses.append(cls)
        subclasses += get_subclasses(cls)

    return subclasses


def get_engines():
    """Return a list containing an instance of each available generator.

    It would be preferable to return the class (not all generators are
    needed), but abstract base classes use properties, not attributes,
    to enforce interface compliance :(

    """

    engines = []
    builtin_dir = os.path.abspath(os.path.dirname(__file__))

    # Import the built-ins only once
    if builtin_dir not in imported_dirs:
        import_engines(builtin_dir)

    log.debug('subclasses=%r', SuggestBase.__subclasses__())
    for klass in get_subclasses(SuggestBase):
        # Ignore base classes
        # if klass.__name__ == 'WordGenBase':
        #     continue
        log.debug('subclass=%r', klass)
        try:
            inst = klass()
            log.debug('Loaded generator : `%s`', inst.name)
        except Exception as err:
            log.error(err)
        else:
            engines.append(inst)

    engines.sort(key=lambda c: c.name)
    return engines
