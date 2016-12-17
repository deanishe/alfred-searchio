#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-01
#

"""Searchio! search engines."""

from __future__ import print_function, unicode_literals, absolute_import

import abc
import imp
import json
import logging
import os
import urllib
import time

from workflow import web

from searchio import util

log = logging.getLogger('workflow.{0}'.format(__name__))

imported_dirs = set()
_imported = set()


def find_engines(dirpath):
    """Find *.py and *.json engine files in `dirpath`.

    The yielded paths may or may not point to valid engine files.

    Args:
        dirpath (str): Directory path.

    Yields:
        str: Paths to .py and .json files.
    """
    dirpath = os.path.abspath(dirpath)
    if not os.path.exists(dirpath):
        return

    for filename in os.listdir(dirpath):
        path = os.path.join(dirpath, filename)
        basename, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext == '.py' and not filename.startswith('_'):
            yield path
        if ext == '.json':
            yield path


class Manager(object):
    """Import and instantiate engine plugins.

    Loads Python/JSON files from specified directories
    and creates Engine objects from the classes/configuration
    in them.

    Pass the directories to search on instantiation or using
    `Manager.load_engines(dirpath)`.

    Access the generated Engine objects with `Manager.engines`
    and `Manager.get_engine(engine_id)`.

    """

    def __init__(self, dirpaths=None):
        """Create new `Manager` object.

        Args:
            dirpaths (iterable, optional): Directories to load engines
                from.
        """
        s = time.time()
        self._dirpaths = set()
        self._imported = set()
        self._engines = {}
        self._engine_classes = set()

        if dirpaths:
            for path in dirpaths:
                self.load_engines(path)
        log.debug('%d engines loaded in %0.3fs',
                  len(self._engines), time.time() - s)

    def load_engines(self, dirpath):
        """Load configurations in `dirpath` and create corresponding objects.

        Args:
            dirpath (str): Path to directory containing engines.
        """

        dirpath = os.path.abspath(dirpath)

        if dirpath in self._dirpaths:
            log.debug('Engines already loaded from %r', dirpath)
            return 0

        for path in find_engines(dirpath):

            if path in self._imported:
                log.debug('Already imported %r', path)
                continue

            log.debug('Reading %r ...', path)

            # Just extension, lowercase, i.e. "py" or "json"
            ext = os.path.splitext(path)[1][1:].lower()
            method_name = '_load_{0}'.format(ext)

            # Call appropriate method
            for engine in getattr(self, method_name)(path):
                if engine.id in self._engines:
                    log.warning('Overriding existing engine %r with %r',
                                self._engines[engine.id], engine)
                self._engines[engine.id] = engine
                log.debug('Loaded "%s" (%d variant(s); id=%s)',
                          engine.name, len(engine.variants), engine.id)

            self._imported.add(path)
            # log.debug('Loaded engines from %r', path)

    def _load_py(self, path):
        """Import Python module and instantiate its Engines.

        Args:
            path (str): Path to .py file containing `Engine`
                subclasses.

        Returns:
            list: `Engine` objects.
        """

        modname = os.path.splitext(os.path.basename(path))[0]
        modname = 'engines.{0}'.format(modname)

        imp.load_source(modname, path)

        # Find newly-added classes and add an instance of each
        # to self._engines.
        for klass in get_subclasses(Engine):
            if klass not in self._engine_classes:
                self._engine_classes.add(klass)
                yield klass(path)

    def _load_json(self, path):
        """Load an Engine from a JSON file.

        Args:
            path (str): Path to JSON file to load.

        Returns:
            list: `Engine` objects based on JSON file.
        """
        return [JSONEngine(path)]

    @property
    def dirpaths(self):
        return tuple(sorted(self._dirpaths))

    @property
    def engines(self):
        return sorted(self._engines.values(), key=lambda e: e.id)

    def get_engine(self, engine_id):
        return self._engines.get(engine_id)

    def _is_builtin(self, path):
        return util.in_same_directory(path, __file__)


class BaseEngine(object):
    """Implements actual search functionality for `Engine`."""

    def __init__(self, path=None):
        self.path = path
        self._icon = None

    def suggest(self, query, variant_id):
        """Return list of unicode suggestions."""
        url = self.get_suggest_url(query, variant_id)
        r = web.get(url)
        log.debug('[%s] %s', r.status_code, r.url)
        r.raise_for_status()
        return self._post_process_response(r.json())

    def _post_process_response(self, response_data):
        return response_data[1]

    @property
    def icon(self):
        """Relative path to icon for Alfred results.

        Assumes icon is in same directory as this Python module and is
        called `<id>.png` where `<id>` is the `id` of the class.
        """
        if not self._icon:
            candidates = ['{}.png'.format(self.id)]
            dp = os.path.dirname(self.path)
            bn = os.path.basename(self.path)
            n, x = os.path.splitext(bn)
            if self.path:
                candidates.append('{}.png'.format(n))
            for filename in candidates:
                p = os.path.join(dp, filename)
                if os.path.exists(p):
                    log.debug('[%s/icon] %r', self.id, p)
                    self._icon = p
                    break
            else:
                self._icon = 'icon.png'

        return self._icon

    def get_suggest_url(self, query, variant_id):
        """URL to fetch suggestions from."""
        if variant_id not in self.variants:
            raise ValueError('Unknown variant : {0!r}'.format(variant_id))
        # TODO: Add GET var replacement/addition?
        variant = self.variants[variant_id]

        rplc = dict(query=query, variant=variant_id)
        rplc.update(variant.get('vars', {}))

        rplc = util.url_encode_dict(rplc)

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
        rplc = util.url_encode_dict(rplc)

        url = variant.get('search_url', self.search_url)
        return url.format(**rplc)

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


class Engine(BaseEngine):
    """Base class for auto-suggestion.

    Subclasses must override `id`, `name`, `suggest_url`, `search_url`
    and `variants` properties.
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
                'search_url': 'https://uk.example.com/search',
                'vars': { 'region': 'uk' }
            },
            ...

        Only name is required.
        """
        return


class JSONEngine(BaseEngine):
    """Engine based on configuration stored in a JSON file.

    Attributes:
        path (str): The JSON file engine's configuration was loaded from.
    """
    def __init__(self, json_path):
        """Create new JSON-based Engine.

        Args:
            json_path (str): Path to JSON configuration file.

        Raises:
            ValueError: Raised if JSON configuration is invalid/incomplete.
        """
        super(JSONEngine, self).__init__(json_path)
        # self.path = json_path
        self._id = None
        self._name = None
        self._suggest_url = None
        self._search_url = None
        self._variants = None

        # Load JSON
        with open(json_path) as fp:
            data = json.load(fp)

        # Ensure JSON configuration is valid
        for key in ('id', 'name', 'suggest_url', 'search_url', 'variants'):
            if key not in data:
                raise ValueError(
                    'Required item {0!r} is missing in {1!r}'.format(
                        key, json_path))

        self._id = data['id']
        self._name = data['name']
        self._suggest_url = data['suggest_url']
        self._search_url = data['search_url']
        self._variants = data['variants']

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def suggest_url(self):
        return self._suggest_url

    @property
    def search_url(self):
        return self._search_url

    @property
    def variants(self):
        return self._variants


def get_subclasses(klass):
    """Return list of all subclasses of `klass`.

    Also recurses into subclasses.

    """

    subclasses = []

    for cls in klass.__subclasses__():
        subclasses.append(cls)
        subclasses += get_subclasses(cls)

    return subclasses
