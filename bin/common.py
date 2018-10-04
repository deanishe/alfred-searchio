#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-13
#

"""Generation utilities."""

from __future__ import print_function, absolute_import

from collections import namedtuple
import os
import re
import sys
from urllib import urlopen
from uuid import uuid4


Lang = namedtuple('Lang', 'code name')


def log(s, *args):
    """Simple STDERR logger."""
    if args:
        s = s % args
    print(s, file=sys.stderr)


def uuid():
    return str(uuid4())


def sanitise_ws(s):
    """Collapse multiple whitespace and trim."""
    return re.sub(r'\s+', ' ', s).strip()


def mkdata(title, description, icon='', variants=None, **kwargs):
    """Return a dictionary initialised for a Search."""
    variants = variants or []
    d = dict(title=title, description=description,
             variants=variants)
    if icon:
        d['icon'] = icon

    if 'jsonpath' in kwargs:
        d['jsonpath'] = kwargs['jsonpath']

    if 'pcencode' in kwargs:
        d['pcencode'] = kwargs['pcencode']

    return d


def mkvariant(uid, name, title, search_url, suggest_url=None,
              icon='', **kwargs):
    """Return a dictionary initialised for a Search."""
    d = dict(uid=uid, name=name, title=title,
             search_url=search_url, suggest_url=suggest_url)
    # if lang:
    #     d['lang'] = lang
    # if country:
    #     d['country'] = country
    if icon:
        d['icon'] = icon

    return d


def datapath(filename):
    """Return path to a file in the data directory."""
    p = os.path.dirname(__file__)
    gp = os.path.dirname(p)
    return os.path.join(gp, 'data', filename)


def httpget(url, cachepath=None):
    """Return contents of `url`.

    Args:
        url (str): URL to read.

    Returns:
        str: Contents of HTTP response.
    """
    if cachepath and os.path.exists(cachepath):
        with open(cachepath) as fp:
            return fp.read()

    data = urlopen(url).read()

    if cachepath:
        with open(cachepath, 'wb') as fp:
            fp.write(data)

    return data


def print_lang(lang, **kwargs):
    s = u'{l.code}\t{l.name}'.format(l=lang).encode('utf-8')
    print(s, **kwargs)
