#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-13
#

"""Searchio! engines."""

from __future__ import print_function, absolute_import

import json
import os
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
        description (unicode): Search engine details
        jsonpath (unicode): JSON path to results
        title (unicode): Name of search engine
        uid (str): UID of engine (usu. based on filename)
    """
    # TODO: Document new models
    # TODO: Add "envvar" o.Ä. for required settings (e.g. for Google Places API key)

    _required = ('title', 'description', 'variants')
    _optional = ('jsonpath',)
    _private = ('variants',)

    @classmethod
    def from_dict(cls, d):
        e = cls(d['uid'])
        return _obj_from_dict(e, d)

    @classmethod
    def from_file(cls, p):
        with open(p) as fp:
            d = json.load(fp)

        d['uid'] = path2uid(p)
        return cls.from_dict(d)

    def __init__(self, uid):
        self.uid = uid
        self.title = u''
        self.description = u''
        self.jsonpath = u'[1]'
        self._variants = []

    @property
    def variants(self):
        return [Variant.from_dict(self, d) for d in self._variants]


class Variant(object):

    _required = ('uid', 'name', 'title', 'search_url')
    _optional = ('suggest_url', 'icon')
    _private = ('uid', 'icon')

    @classmethod
    def from_dict(cls, engine, d):
        v = cls(engine)
        return _obj_from_dict(v, d)

    def __init__(self, engine):
        self._engine = weakref.ref(engine)
        self._uid = ''
        self.name = ''
        self.title = ''
        self.search_url = ''
        self.suggest_url = ''
        self._icon = ''

    @property
    def engine(self):
        return self._engine()

    @property
    def uid(self):
        return '{}-{}'.format(self.engine.uid, self._uid)

    @property
    def icon(self):
        return self._icon

    @property
    def jsonpath(self):
        return self.engine.jsonpath

    @property
    def search(self):
        return Search.from_variant(self)


class Search(object):

    _required = ('title', 'icon', 'jsonpath', 'search_url')
    _optional = ('suggest_url',)
    _private = ()

    @classmethod
    def from_variant(cls, v):
        s = cls(v.uid)

        for k in cls._required + cls._optional:
            setattr(s, k, getattr(v, k))

        return s

    @classmethod
    def from_dict(cls, d):
        s = cls(d['uid'])
        return _obj_from_dict(s, d)

    @classmethod
    def from_file(cls, p):
        s = cls(path2uid(p))

        with open(p) as fp:
            d = json.load(fp)

        return _obj_from_dict(s, d)

    def __init__(self, uid):
        self.uid = uid
        self.title = ''
        self.icon = ''
        self.jsonpath = '[1]'
        self.search_url = ''
        self.suggest_url = ''

    @property
    def dict(self):
        d = dict(title=self.title, icon=self.icon,
                 jsonpath=self.jsonpath,
                 search_url=self.search_url)

        if self.suggest_url:
            d['suggest_url'] = self.suggest_url

        return d
