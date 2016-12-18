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
from collections import OrderedDict
import imp
import json
import logging
import os
import urllib
import time

from workflow import web

from searchio import util

log = logging.getLogger(__name__)

imported_dirs = set()
_imported = set()


def find_engines(dirpath):
    """Find *.py and *.json engine files in ``dirpath``.

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

    `Manager.load_engines() *must* be called to import the
    engines.

    Access the generated Engine objects with `Manager.engines`
    and `Manager.get_engine(engine_id)`.

    """

    def __init__(self, dirpaths=None):
        """Create new `Manager` object.

        Args:
            dirpaths (iterable, optional): Directories to load engines
                from.
        """
        self._dirpaths = OrderedDict()
        self._engines = {}

        if dirpaths:
            for dirpath in dirpaths:
                self.add_directory(dirpath)
                # self.load_engines(path)

    def add_directory(self, dirpath):
        """Add plugin directory.

        Args:
            dirpath (str): Path to directory containing engines.
        """
        if os.path.isdir(dirpath):
            self._dirpaths[dirpath] = True

    def load_engines(self, dirpaths=None):
        """Load configurations in `dirpath` and create corresponding objects.

        Args:
            dirpaths (list, optional): Paths to directories containing engines.
        """
        dirpaths = dirpaths or []
        for p in dirpaths:
            self.add_directory(p)

        start = time.time()
        engines = {}

        filepaths = []

        # Find files
        for dirpath in self.dirpaths:

            for path in find_engines(dirpath):
                if path not in filepaths:
                    filepaths.append(path)
                # Just extension, lowercase, i.e. "py" or "json"
                # ext = os.path.splitext(path)[1][1:].lower()
                # if ext in ('json', 'py'):
                #     filepaths.append(path)

        # Load collected files
        def _add_engine(engine):
            if engine.id in engines:
                log.warning('Overriding existing engine %r with %r',
                            engines[engine.id], engine)

            engines[engine.id] = engine
            log.debug('[engines/load] id=%s, name="%s", variants=%d',
                      engine.id, engine.name, len(engine.variants))

        imported = set()
        for p in filepaths:
            if p in imported:
                continue

            imported.add(p)
            log.debug('[engines/load] %s ...', p)

            if p.lower().endswith('.json'):
                _add_engine(JSONEngine(p))
            else:
                self._loadpy(p)

        # Find newly-added classes and add an instance of each
        # to self._engines.
        seen = set()
        for klass in get_subclasses(Engine):
            if klass not in seen:
                seen.add(klass)
                _add_engine(klass(path))

        log.debug('[engines/load] %d engine(s) in %0.3fs',
                  len(engines), time.time() - start)

        self._engines = engines

    def _loadpy(self, path):
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

    @property
    def dirpaths(self):
        """Engine directories.

        Searched for .py and .js files defining engines when
        `Manager.load_engines()` is called.

        Returns:
            list: Unicode paths to engine directories.
        """
        return self._dirpaths.keys()

    @property
    def engines(self):
        """Loaded `Engine` objects.

        Populated by `Manager.load_engines`.

        Returns:
            list: Sequence of `Engine` instances.
        """
        return sorted(self._engines.values(), key=lambda e: e.id)

    def get_engine(self, engine_id):
        """Return `Engine` instance for ID.

        Args:
            engine_id (str): Engine ID.

        Returns:
            Engine: Engine for this ID or `None`
        """
        return self._engines.get(engine_id)

    def get_variant(self, engine_id, variant_id):
        """Return `Variant` for engine and variant IDs.

        Args:
            engine_id (str): Engine ID.
            variant_id (str): Variant ID

        Returns:
            Variant: Corresponding `Variant`

        Raises:
            ValueError: If engine or variant IDs are unknown
        """
        engine = self.get_engine(engine_id)
        if not engine:
            raise ValueError('Unknown engine: {!r}'.format(engine_id))

        if variant_id not in engine.variants:
            if '*' in engine.variants:
                variant_id = '*'
            else:
                raise ValueError('Unknown variant for {!r} : {!r}'.format(
                    engine.name, variant_id))

        return engine.variants[variant_id]

    def _is_builtin(self, path):
        return util.in_same_directory(path, __file__)


class BaseEngine(object):
    """Implements actual search functionality for `Engine`."""

    # TODO: Default to URL still containing '{query}'
    _placeholder = u'QXQXQXQX'

    def __init__(self, path=None):
        self.path = path
        self._icon = None

    def suggest(self, variant_id, query):
        """Return list of unicode suggestions."""
        url = self.get_suggest_url(query, variant_id)
        r = web.get(url)
        log.debug('[%s] %s', r.status_code, r.url)
        r.raise_for_status()
        return self._post_process_response(r.json())

    def _post_process_response(self, response_data):
        return response_data[1]

    @property
    def title_scheme(self):
        """Scheme for "Engine name (variant name)"."""
        return u'{engine.name} ({variant.name})'

    @property
    def icon(self):
        """Relative path to icon for Alfred results.

        Assumes icon is in same directory as this Python module and is
        called `<id>.png` where `<id>` is the `id` of the class.
        """
        if not self._icon:
            candidates = ['{}.png'.format(self.id)]
            if self.path:
                n = os.path.basename(self.path)
                candidates.append('{}.png'.format(os.path.splitext(n)[0]))

            for filename in candidates:
                p = filename
                if self.path:
                    p = os.path.join(os.path.dirname(self.path), filename)

                if os.path.exists(p):
                    log.debug('[engines/%s/icon] %r', self.id, p)
                    self._icon = p
                    break
            else:
                log.warning('[engines/%s/icon] No icon', self.id)
                self._icon = 'icon.png'

        return self._icon

    def get_suggest_url(self, variant_id, query=None):
        """URL to fetch suggestions from."""
        if variant_id not in self.variants:
            if '*' in self.variants:
                variant_id = '*'
            else:
                raise ValueError('Unknown variant : {!r}'.format(variant_id))
        # TODO: Add GET var replacement/addition?
        variant = self.variants[variant_id]

        query = query or self._placeholder

        rplc = dict(query=query, variant=variant_id)
        rplc.update(variant.get('vars', {}))

        rplc = util.url_encode_dict(rplc)

        url = variant.get('suggest_url', self.suggest_url)
        return url.format(**rplc).replace(self._placeholder, u'{query}')

    def get_search_url(self, variant_id, query=None):
        """URL for full search results (webpage)."""
        if variant_id not in self.variants:
            if '*' in self.variants:
                variant_id = '*'
            else:
                raise ValueError('Unknown variant : {!r}'.format(variant_id))
        # TODO: Add GET var replacement/addition?
        variant = self.variants[variant_id]

        query = query or self._placeholder

        rplc = {'query': query, 'variant': variant_id}
        rplc.update(variant.get('vars', {}))
        rplc = util.url_encode_dict(rplc)

        url = variant.get('search_url', self.search_url)
        return url.format(**rplc).replace(self._placeholder, u'{query}')

    def search(self, variant_id, query):
        """Synonym for `suggest()`."""
        return self.suggest(query, variant_id)

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
    def title_scheme(self):
        """Format pattern for human-readable title of variants.

        E.g. ``'{engine.name} {variant.name}'`` to produce
        ``'Amazon Deutschland'`` or ``'{engine.name} ({variant.name})'``
        to get ``'Google (Deutsch)'``

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
        self._title_scheme = None
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

        # Required keys
        self._id = data['id']
        self._name = data['name']
        self._suggest_url = data['suggest_url']
        self._search_url = data['search_url']
        self._variants = data['variants']

        # Optional keys
        self._title_scheme = (data.get('title_scheme') or
                              u'{engine.name} ({variant[name]})')

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def title_scheme(self):
        return self._title_scheme

    @property
    def suggest_url(self):
        return self._suggest_url

    @property
    def search_url(self):
        return self._search_url

    @property
    def variants(self):
        variants = {}
        for id_, d in self._variants.items():
            if 'title' not in d:
                s = self.title_scheme.format(engine=self, variant=d)
                d['title'] = s
            variants[id_] = d

        return variants


def get_subclasses(klass):
    """Return list of all subclasses of `klass`.

    Also recurses into subclasses.

    """

    subclasses = []

    for cls in klass.__subclasses__():
        subclasses.append(cls)
        subclasses += get_subclasses(cls)

    return subclasses
