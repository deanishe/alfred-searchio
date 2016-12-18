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
"""

from __future__ import print_function, unicode_literals, absolute_import

import os
import sys
from urllib import urlopen


def log(s, *args):
    """Simple STDERR logger."""
    if args:
        s = s % args
    print(s, file=sys.stderr)


def datapath(filename):
    """Return path to a file in the data directory."""
    p = os.path.dirname(__file__)
    gp = os.path.dirname(p)
    return os.path.join(gp, filename)


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
