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
import imp
import json
import logging
import os
import urllib
import sys

from workflow import web

log = logging.getLogger('workflow.{0}'.format(__name__))

imported_dirs = set()
_imported = set()

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


def in_same_directory(*paths):
    paths = [os.path.abspath(p) for p in paths]
    parent = None
    for path in paths:
        if not parent:
            parent = os.path.dirname(path)

        elif os.path.dirname(path) != parent:
            return False

    return True


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

    def __init__(self, dirpaths=None):
        self._dirpaths = set()
        self._imported = set()
        self._engines = {}
        self._engine_classes = set()

        if dirpaths:
            for path in dirpaths:
                self.load_engines(path)

    def load_engines(self, dirpath):
        dirpath = os.path.abspath(dirpath)

        if dirpath in self._dirpaths:
            log.debug('Engines already loaded from %r', dirpath)
            return 0

        for path in find_engines(dirpath):

            if path in self._imported:
                log.debug('Already imported %r', path)
                continue

            log.debug('Loading engines from %r ...', path)

            # Just extension, lowercase, i.e. "py" or "json"
            ext = os.path.splitext(path)[1][1:].lower()
            method_name = '_load_{0}'.format(ext)

            log.debug('engines=%r', self._engines)

            # Call appropriate method
            for engine in getattr(self, method_name)(path):
                if engine.id in self._engines:
                    log.warning('Overriding existing engine %r with %r',
                                self._engines[engine.id], engine)
                self._engines[engine.id] = engine

            self._imported.add(path)
            log.debug('Loaded engine from %r', path)
            log.debug('engines=%r', self._engines)

    def _load_py(self, path):

        modname = os.path.splitext(os.path.basename(path))[0]
        if self._is_builtin(path):
            modname = 'engines.builtin.{0}'.format(modname)
        else:
            modname = 'engines.user.{0}'.format(modname)

        imp.load_source(modname, path)

        # Find newly-added classes and add an instance of each
        # to self._engines.
        for klass in get_subclasses(Engine):
            if klass not in self._engine_classes:
                self._engine_classes.add(klass)
                yield klass()

    def _load_json(self, path):

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
        return in_same_directory(path, __file__)


class BaseEngine(object):

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
        # TODO: Add GET var replacement/addition?
        variant = self.variants[variant_id]

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
                'search_url': 'https://uk.example.com/search',
                'vars': { 'region': 'uk' }
            },
            ...

        Only name is required.
        """
        return


class JSONEngine(BaseEngine):

    def __init__(self, json_path):
        self.path = json_path
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



def _get_engine_modules(dirpath):
    """Return list of files in dirpath matching `*.py`"""

    modnames = []

    for filename in os.listdir(dirpath):
        if filename.endswith('.py') and not filename.startswith('_'):
            name = os.path.splitext(filename)[0]
            modnames.append(name)

    return modnames


def import_engines(dirpath):
    """Import Python modules in `dirpath`.

    Import *.py files in `dirpath`. Files starting with _ (underscore)
    are ignored.

    Builtins (i.e. .py files in the `engines` package) are imported
    as `engines.<modname>`. Other files are imported as
    `engines.user.<modname>`.

    Args:
        dirpath (str): Directory path.
    """
    dirpath = os.path.abspath(dirpath)

    # Is `dirpath` this package?
    builtin = dirpath == os.path.abspath(os.path.dirname(__file__))

    for filename in os.listdir(dirpath):
        if not filename.endswith('.py') or filename.startswith('_'):
            continue

        path = os.path.join(dirpath, filename)
        if path in _imported:
            log.debug('Already imported %r', path)
            continue

        modname = os.path.splitext(filename)[0]
        if builtin:
            modname = 'engines.{}'.format(modname)
        else:
            modname = 'engines.user.{}'.format(modname)
        imp.load_source(modname, path)
        _imported.add(path)
        log.debug('Loaded engines from %r', path)


def import_engines_old(dirpath):
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
    # TODO: Create engines from JSON files.
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
