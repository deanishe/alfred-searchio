#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-13
#

"""
Searchio! engines.
==================

Data models and JSON config files for built-in engines.

There are 3 models: `Engine`, `Variant` and `Search`.

An `Engine` represents a single search engine, e.g. "Google" or
"Wikipedia" and is generated from a JSON configuration file.

An `Engine` provides one or more variants. A `Variant`
represents a language- or region-specific search, e.g.
"Google English" or "Amazon Deutschland". The `Variant`
model is for displaying in Alfred.

Each `Variant` exports a `Search`, which is the actual
model for fetching search suggestions and open search
results.

"""

from __future__ import print_function, absolute_import

import json
import weakref

from searchio.util import path2uid

__all__ = [
    'load',
    'Engine',
    'Variant',
    'Search',
]


def load(*dirpaths):
    """Load Engines from directories.

    Args:
        *dirpaths (str): Directories to load JSON engine defs from.

    """
    from searchio.util import FileFinder
    engines = []
    f = FileFinder(dirpaths, ['json'])
    for p in f:
        e = Engine.from_file(p)
        engines.append(e)

    engines.sort(key=lambda e: e.title)

    return engines


def _obj_from_file(o, p):
    """Unserialise JSON file and call `_obj_from_dict()`.

    Args:
        o (object): Python object
        p (str): Path to JSON file

    Returns:
        object: Updated object

    """
    with open(p) as fp:
        return _obj_from_dict(json.load(fp))


def _obj_from_dict(o, d):
    """Populate objects attributes from dict.

    Args:
        o (object): Python object
        d (dict): Dict to update object from

    Returns:
        object: Updated object

    Raises:
        ValueError: Raised if required key is missing

    """
    for k in o._required:
        if k in d:
            n = '_' + k if k in o._private else k
            setattr(o, n, d[k])
        else:
            raise ValueError('Required key "{}" missing: {}'.format(k, d))

    for k in o._optional:
        if k in d:
            n = '_' + k if k in o._private else k
            setattr(o, n, d[k])
    return o


class Engine(object):
    """Search engine. Provides one or more `Variants`.

    Attributes:
        description (unicode): Search engine details, e.g. "Image search"
        jsonpath (unicode): JSON path to results. The default ``$[1][*]``
            is appropriate for OpenSearch results.
        title (unicode): Name of search engine.
        uid (str): UID of engine (usu. based on filename).

    """
    # TODO: Document new models
    # TODO: Add "envvar" o.Ä. for required settings (e.g. for Google Places API key)

    # Required settings
    _required = ('title', 'description', 'variants')
    # Optional settings
    _optional = ('jsonpath', 'pcencode')
    # Settings that should be assigned to private attributes,
    # e.g. "_attribute", not "attribute".
    _private = ('variants',)

    @classmethod
    def from_dict(cls, d):
        """Create a new `Engine` from a dictionary.

        Args:
            d (dict): Mapping of required values inc. ``uid``.

        Returns:
            Engine: Engine generated from dict.

        """
        e = cls(d['uid'])
        return _obj_from_dict(e, d)

    @classmethod
    def from_file(cls, p):
        """Create a new `Engine` from a JSON file.

        Args:
            p (str): Path to JSON file.

        Returns:
            Engine: Configured engine.

        """
        with open(p) as fp:
            d = json.load(fp)

        d['uid'] = path2uid(p)
        return cls.from_dict(d)

    def __init__(self, uid):
        """Create a new `Engine`.

        Args:
            uid (str): UID for engine.

        """
        self.uid = uid
        self.title = u''
        self.description = u''
        self.jsonpath = u'$[1][*]'
        self.pcencode = False
        self._variants = []

    @property
    def variants(self):
        """Engine variants.

        Returns:
            list: Sequence of `Variant` objects for this engine.

        """
        return [Variant.from_dict(self, d) for d in self._variants]


class Variant(object):
    """A concrete variant of a search engine.

    Variants contain actual suggestion & search URLs.

    Attributes:
        name (unicode): Short name of the variant, e.g. "English"
            or "Switzerland".
        search_url (str): URL for search results (including placeholder(s))
        suggest_url (str): URL for search suggestions (including placeholder(s))
        title (unicode): Full name of the variant, e.g. "Google (English)"
            or "Amazon Deutschland".

    """
    _required = ('uid', 'name', 'title', 'search_url')
    _optional = ('suggest_url', 'icon')
    _private = ('uid', 'icon')

    @classmethod
    def from_dict(cls, engine, d):
        """Create a new `Variant` from an `Engine` and a `dict`.

        Args:
            engine (Engine): Engine this variant belongs to.
            d (dict): Variant settings.

        Returns:
            Variant: Variant configured from dict ``d``.

        """
        v = cls(engine)
        return _obj_from_dict(v, d)

    def __init__(self, engine):
        """Create new `Variant` for `Engine`.

        A weak reference to ``engine`` is retained.

        Args:
            engine (Engine): Engine this variant belongs to.

        """
        self._engine = weakref.ref(engine)
        self._uid = ''
        self.name = ''
        self.pcencode = engine.pcencode
        self.title = ''
        self.search_url = ''
        self.suggest_url = ''
        self._icon = ''

    @property
    def engine(self):
        """The `Engine` this `Variant` belongs to.

        Returns:
            Engine: Variant's engine.

        """
        return self._engine()

    @property
    def uid(self):
        """Full UID of variant. Includes engine's UID.

        Returns:
            str: Variant UID of form `<engine-uid>-<variant-uid>`.

        """
        return '{}-{}'.format(self.engine.uid, self._uid)

    @property
    def icon(self):
        """Variant's icon.

        Returns:
            str: Path to image file.

        """
        return self._icon

    @property
    def jsonpath(self):
        """JSON Path to extract results.

        Returns:
            unicode: JSON Path.

        """
        return self.engine.jsonpath

    @property
    def search(self):
        """A `Search` object based on this variant.

        Returns:
            Search: Search for this variant.

        """
        return Search.from_variant(self)


class Search(object):
    """Configuration for retrieving search suggestions.

    Attributes:
        icon (str): Path to icon file.
        jsonpath (unicode): JSON Path for extracting suggestions from
            API responses.
        keyword (str): Script Filter keyword.
        pcencode (bool): Whether to use percent encoding (instead
            of plus encoding).
        search_url (str): URL for search results.
        suggest_url (str): URL for search suggestions.
        title (unicode): Full search title, e.g. "Google (English)".
        uid (str): UID of search. This is a combination of engine and
            variant UIDs.

    """
    _required = ('title', 'icon', 'jsonpath', 'search_url')
    _optional = ('pcencode', 'suggest_url', 'keyword')
    _private = ()

    @classmethod
    def from_variant(cls, v):
        """Create a new `Search` from a `Variant`.

        Args:
            v (Variant): Variant to base `Search` on.

        Returns:
            Search: Search based on `Variant`.

        """
        s = cls(v.uid)

        for k in cls._required + cls._optional:
            setattr(s, k, getattr(v, k))

        return s

    @classmethod
    def from_dict(cls, d):
        """Create a new `Search` from a `dict`.

        Dict must contain a ``uid`` in addition to
        usual required options.

        Args:
            d (dict): `Search` configuration.

        Returns:
            Search: Search configured from dict ``d``.

        """
        s = cls(d['uid'])
        return _obj_from_dict(s, d)

    @classmethod
    def from_file(cls, p):
        """Create a `Search` from a JSON file.

        Args:
            p (str): Path to JSON search config.

        Returns:
            Search: Search configured from JSON file.

        """
        s = cls(path2uid(p))

        with open(p) as fp:
            d = json.load(fp)

        return _obj_from_dict(s, d)

    def __init__(self, uid):
        """Create new `Search` with given UID.

        Args:
            uid (str): UID for the `Search`.

        """
        self.uid = uid
        self.title = ''
        self.icon = ''
        self.keyword = ''
        self.jsonpath = '[1]'
        self.pcencode = False
        self.search_url = ''
        self.suggest_url = ''

    @property
    def dict(self):
        """Dict suitable for serialising to JSON.

        Returns:
            dict: Configuration for this `Search`.

        """
        d = dict(title=self.title, icon=self.icon,
                 keyword=self.keyword,
                 jsonpath=self.jsonpath,
                 search_url=self.search_url)

        if self.pcencode:
            d['pcencode'] = self.pcencode

        if self.suggest_url:
            d['suggest_url'] = self.suggest_url

        return d
