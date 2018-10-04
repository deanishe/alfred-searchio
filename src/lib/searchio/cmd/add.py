#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-17
#

"""searchio add [options] <title> <url>

Display help message for command(s).

Usage:
    searchio add [-s <url>] [-i <path>] [-j <jpath>] [-u <uid>] [-p] <keyword> <title> <url>
    searchio add --env
    searchio add -h

Options:
    -e, --env                  Read input from environment variables
    -i, --icon <path>          Path of icon for search
    -j, --json-path <jpath>    JSON path for results
    -p, --pcencode             Whether to percent-encode query
    -s, --suggest <url>        URL for suggestions
    -u, --uid <uid>            Search UID
    -h, --help                 Display this help message
"""

from __future__ import print_function, absolute_import

import json
import os

from docopt import docopt
from workflow.notify import notify

from searchio.core import Context
from searchio import engines
from searchio import util

log = util.logger(__name__)


def usage(wf=None):
    """CLI usage instructions."""
    return __doc__


def parse_args(wf, args):
    """Build search `dict` from `docopt` ``args``.

    Args:
        wf (workflow.Workflow3): Current workflow
        args (docopt.Args): Arguments returned by `docopt`

    Returns:
        searchio.engines.Search: Search object

    """
    params = [
        # search dict key | envvar name | CLI option | default
        ('keyword', 'keyword', '<keyword>', ''),
        ('uid', 'uid', '--uid', util.uuid()),
        ('pcencode', 'pcencode', '--pcencode', False),
        ('title', 'title', '<title>', ''),
        ('search_url', 'search_url', '<url>', ''),
        ('suggest_url', 'suggest_url', '--suggest', ''),
        ('icon', 'icon', '--icon', ''),
        ('jsonpath', 'jsonpath', '--json-path', '[1]'),
    ]

    d = {}
    for k, kenv, opt, default in params:
        if args.get('--env'):
            v = os.getenv(kenv, default)
            if default in (True, False):
                if v == '1':
                    v = True
                else:
                    v = False
        else:
            v = args.get(opt) or default

        if default not in (True, False):
            v = wf.decode(v).strip()

        d[k] = v

    return d


def run(wf, argv):
    """Run ``searchio add`` sub-command."""
    args = docopt(usage(wf), argv)
    ctx = Context(wf)
    d = parse_args(wf, args)

    s = engines.Search.from_dict(d)

    if not util.valid_url(d['search_url']):
        raise ValueError('Invalid search URL: {!r}'.format(d['search_url']))

    if d['suggest_url'] and not util.valid_url(d['suggest_url']):
        raise ValueError('Invalid suggest URL: {!r}'.format(d['suggest_url']))

    p = ctx.search(s.uid)

    with open(p, 'wb') as fp:
        json.dump(s.dict, fp, sort_keys=True, indent=2)
    # m.save(**d)

    log.debug('Adding new search to info.plist ...')

    notify('Added New Search', d['title'])
