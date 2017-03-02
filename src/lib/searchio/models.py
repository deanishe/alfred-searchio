#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-18
#

"""Abstract and concrete data models."""

from __future__ import print_function, absolute_import

import abc
import hashlib
import json
import os
import weakref

from searchio import util, IMAGE_EXTENSIONS

log = util.logger(__name__)


def _findicon(path):
    dpath = os.path.dirname(path)
    bn = os.path.splitext(os.path.basename(path))[0]
    for fn in ['{}{}'.format(bn, x) for x in IMAGE_EXTENSIONS]:
        p = os.path.join(dpath, fn)
        if os.path.exists(p):
            return p
    return None


def _absicon(fn, dirpath=None):
    dirpath = dirpath or os.getcwd()
    if os.path.isabs(fn):
        return fn

    if os.path.isfile(dirpath):
        dirpath = os.path.dirname(dirpath)

    p = os.path.join(dirpath, fn)
    return p


class AttrDict(dict):
    """Dictionary whose keys are also accessible as attributes."""

    def __init__(self, *args, **kwargs):
        """Create new `AttrDict`.

        Args:
            *args (objects): Arguments to `dict.__init__()`
            **kwargs (objects): Keyword arguments to `dict.__init__()`

        """
        super(AttrDict, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        """Look up attribute as dictionary key.

        Args:
            key (str): Dictionary key/attribute name.

        Returns:
            obj: Dictionary value for `key`.

        Raises:
            AttributeError: Raised if `key` isn't in dictionary.

        """
        if key not in self:
            raise AttributeError(
                "AttrDict object has no attribute '{}'".format(key))

        return self[key]

    def __setattr__(self, key, value):
        """Add `value` to the dictionary under `key`.

        Args:
            key (str): Dictionary key/attribute name.
            value (obj): Value to store for `key`.

        """
        self[key] = value


class ISearch2(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def id(self):
        """Simple, but unique ID to be specified by generated searches."""
        return

    @abc.abstractproperty
    def searches(self):
        """Searches provided by this engine.

        Returns:
            list: Searches
        """
        return

    @abc.abstractmethod
    def handle(self, data):
        """Handle data returned by API.

        Args:
            data (str): Raw API response.

        Returns:
            list: Suggestions returned by API.
        """
        return


class Search2(ISearch2):

    def handle(self, data):
        """Return OpenSearch suggestions."""
        return [s for s in data[1]]


class IEngine(object):
    """A `SearchProvider` provides one or more `Searchers`.

    For instance, "Google" would be a `SearchProvider`,
    "Google (English)" would be a `Searcher`.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def uid(self):
        """Computer-friendly, short name.

        E.g. "ebay" or "google-images".
        """
        return

    @abc.abstractproperty
    def icon(self):
        """Path to PNG icon."""
        return

    @abc.abstractproperty
    def title(self):
        """Longer, human-friendly title.

        E.g. "eBay" or "Google Images".
        """
        return

    @abc.abstractproperty
    def description(self):
        """Description of search.

        E.g. "Game of Thrones fansite"
        """
        return

    @abc.abstractproperty
    def searches(self):
        """Return provided `Search` objects."""
        return

    @abc.abstractmethod
    def search(self, name=None):
        """Return `Search` for ``name``.

        Return default if ``name`` is `None` or missing.
        """
        return


class Engine(IEngine):
    """A `SearchProvider` provides one or more `Searchers`.

    For instance, "Google" would be a `SearchProvider`,
    "Google (English)" would be a `Searcher`.
    """

    _required_props = ('uid', 'title', 'description', 'searches')
    _instances = set()

    def __init__(self, uid=None, title=None, description=None,
                 icon=None, **kwargs):
        self._icon = icon
        self._uid = uid
        self._title = title
        self._description = description
        self._instances.add(weakref.ref(self))

    @classmethod
    def instances(cls):
        """Yield all instances of this class."""
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                log.debug('[engine/dead]')
                dead.add(ref)
        cls._instances -= dead

    @property
    def uid(self):
        """Computer-friendly, short name.

        E.g. "ebay" or "google-images".
        """
        return self._uid

    @property
    def icon(self):
        """Path to PNG icon."""
        return self._icon

    @property
    def title(self):
        """Longer, human-friendly title.

        E.g. "eBay" or "Google Images".
        """
        return self._title

    @property
    def description(self):
        """Description of search.

        E.g. "Game of Thrones fansite"
        """
        return self._description

    @property
    def searches(self):
        """Return provided `Search` objects."""
        return

    def search(self, name=None):
        """Return `Searcher` for ``name``.

        Return default if ``name`` is `None` or missing.
        """
        return

    def validate(self):
        """Raise `ValueError` if a required setting is missing."""
        for k in self._required_props:
            if not getattr(self, k):
                raise ValueError('required value "{}" is not set'.format(k))
        if not isinstance(self.searches, list):
            raise ValueError('"searches" must be `list` not `{}`'.format(
                             self.searches.__class__.__name__))

    def __repr__(self):
        return 'Engine({e.title!r}<{e.uid}>)'.format(e=self)

    def __str__(self):
        return '{!r} ({})'.format(e=self)


class ISearch(object):
    """Provide suggestions and/or search URLs."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def uid(self):
        """Deterministically unique UID.

        E.g. MD5/SHA1 hash.
        """
        return

    @abc.abstractproperty
    def icon(self):
        """Path to PNG icon."""
        return

    @abc.abstractproperty
    def title(self):
        """Longer, human-friendly title.

        E.g. "eBay" or "Google Images".
        """
        return

    @abc.abstractproperty
    def description(self):
        """Description of search.

        E.g. "Game of Thrones fansite"
        """
        return

    @abc.abstractproperty
    def lang(self):
        """The ISO-XXX language supported by this `Searcher`.

        Return `None` or empty string if no specific language is supported.
        """
        return

    @abc.abstractproperty
    def country(self):
        """The ISO-XXX country code supported by this `Searcher`.

        Return `None` or empty string if no specific language is supported."""
        return

    @abc.abstractproperty
    def suggest_url(self):
        """URL for search suggestions.

        Should contain ``{query}`` placeholder.
        """
        return

    @abc.abstractproperty
    def search_url(self):
        """URL for search results in browser.

        Should contain ``{query}`` placeholder.
        """
        return


class Search(ISearch):
    """Provide suggestions and/or search URLs."""

    _required_props = ('uid', 'title', 'description', 'search_url')
    _instances = set()

    def __init__(self, **kwargs):
        """Populate new `Searcher` from ``kwargs``.

        Args:
            **kwargs (dict): Searcher values.
        """
        self._uid = None
        self._title = None
        self._description = None
        self._suggest_url = None
        self._search_url = None
        self._icon = None
        self._lang = None
        self._country = None
        self._path = None
        if kwargs:
            self.update(kwargs)
        self._instances.add(weakref.ref(self))

    @classmethod
    def instances(cls):
        """Yield all instances of this class."""
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    def update(self, data):
        for k in ('uid', 'title', 'description', 'suggest_url',
                  'search_url', 'icon', 'lang', 'country', 'path'):
            if k in data:
                setattr(self, '_{}'.format(k), data[k])

    @property
    def uid(self):
        """Deterministically unique UID.

        E.g. MD5/SHA1 hash.
        """
        if self._uid is None:
            k = u'{}'.format(self.search_url)
            h = hashlib.md5(k.encode('utf-8')).hexdigest()
            log.debug('url=%r, uid=%r', k, h)
            self._uid = h
        return self._uid

    @property
    def icon(self):
        """Path to PNG icon."""
        if self._icon and not os.path.isabs(self._icon):
            pass
        return self._icon

    @property
    def title(self):
        """Longer, human-friendly title.

        E.g. "eBay" or "Google Images".
        """
        return self._title

    @property
    def description(self):
        """Description of search.

        E.g. "Game of Thrones fansite"
        """
        return self._description

    @property
    def lang(self):
        """The ISO-XXX language supported by this `Searcher`.

        Return `None` or empty string if no specific language is supported.
        """
        return self._lang

    @property
    def country(self):
        """The ISO-XXX country code supported by this `Searcher`.

        Return `None` or empty string if no specific language is supported."""
        return self._country

    @property
    def suggest_url(self):
        """URL for search suggestions.

        Should contain ``{query}`` placeholder.
        """
        return self._suggest_url

    @property
    def search_url(self):
        """URL for search results in browser.

        Should contain ``{query}`` placeholder.
        """
        return self._search_url

    def validate(self):
        """Raise `ValueError` if a required setting is missing."""
        for k in self._required_props:
            if not getattr(self, k):
                raise ValueError('required value "{}" is not set'.format(k))

    def __str__(self):
        return '{s.description!r} | {s.search_url}'.format(s=self)

    def __repr__(self):
        return ('Search(uid={s.uid!r}, title={s.title!r}, '
                'description={s.description!r}, '
                'search_url={s.search_url!r})'.format(s=self))


class JSONEngine(Engine):
    """Loads engines from a JSON file."""

    def __init__(self, path):
        """Load engines from JSON file at ``path``."""
        super(JSONEngine, self).__init__()
        self.path = path
        self._searches = []
        with open(path) as fp:
            self._update(json.load(fp))

    def _update(self, data):
        # TODO: Make relative icon paths absolute
        for k in ('uid', 'title', 'description', 'icon'):
            if k in data:
                v = data[k]
                setattr(self, '_{}'.format(k), v)

        if 'searches' in data:
            searches = []
            for d in data['searches']:
                s = Search(**d)

                if not s.icon:
                    s.update({'icon': self.icon})

                if s.icon and not os.path.isabs(s.icon):
                    icon = _absicon(s.icon, self.path)
                    s.update({'icon': icon})
                # log.debug('%s', s)
                searches.append(s)

            self._searches = searches
            log.debug('[engines/%s/load] %d search(es)',
                      self.uid, len(searches))

        self.data = data

    @property
    def icon(self):
        if not self._icon:  # Try to find one
            self._icon = _findicon(self.path)
        elif not os.path.isabs(self._icon):
            self._icon = _absicon(self._icon, self.path)

        return self._icon

    @property
    def searches(self):
        return self._searches
