#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-17
#

"""searchio variants <engine> [<query>]

Display (and optionally filter) variants of an
engine.

Usage:
    searchio variants [-t] <engine> [<query>]
    searchio variants -h

Options:
    -t, --text          Print results as text, not Alfred JSON
    -h, --help          Display this help message
"""

from __future__ import print_function, absolute_import

from collections import namedtuple
import sys

from docopt import docopt

from searchio.core import Context
from searchio import engines
from searchio import util

log = util.logger(__name__)

_text_help = """\
Engine "{engine.title}" provides the following searches.

To specify a when searching, use:
    searchio search <search-id> <query>

"""

# Simple data model
Variant = namedtuple('Variant', 'id name')


def usage(wf):
    """CLI usage instructions."""
    return __doc__


def run(wf, argv):
    """Run ``searchio variants`` sub-command."""
    args = docopt(usage(wf), argv)
    ctx = Context(wf)
    engine_id = wf.decode(args.get('<engine>') or '').strip()
    query = wf.decode(args.get('<query>') or '').strip()
    ICON_BACK = ctx.icon('back')

    engs = engines.load(*ctx.engine_dirs)
    for e in engs:
        if e.uid == engine_id:
            engine = e
            break
    else:
        raise ValueError('Unknown engine : {!r}'.format(engine_id))

    # get user searches so we can highlight already-installed searches
    uids = set([util.path2uid(p) for p in
                util.FileFinder([ctx.searches_dir], ['json'])])

    log.debug('engine=%r', engine)
    variants = engine.variants

    def _key(s):
        return u'{} {}'.format(s.uid, s.title.lower())

    if query:
        variants = wf.filter(query, variants, _key)
    else:
        it = wf.add_item(
            u'All Engines \U00002026',
            u'Go back to engine list',
            arg=engine.uid,
            valid=True,
            icon=ICON_BACK)
        it.setvar('action', 'back')

        variants.sort()

    # ---------------------------------------------------------
    # Show results

    if args.get('--text') or util.textmode():  # Display for terminal

        print(_text_help.format(engine=engine), file=sys.stderr)

        table = util.Table([u'ID', u'Installed', u'Title'])
        for v in variants:
            installed = (u'', u'yes')[v.uid in uids]
            table.add_row((v.uid, installed, v.title))

        print(table)
        print()

    else:  # Display for Alfred
        wf.setvar('action', 'new')
        # TODO: Delimited browse action instead of nested Script Filters?
        icon = ctx.icon(engine.uid)

        for v in variants:
            it = wf.add_item(
                v.title,
                u'{} > {}'.format(engine.title, v.name),
                arg=v.uid,
                valid=True,
                icon=icon)
            it.setvar('engine', engine.uid)
            it.setvar('uid', v.uid)
            it.setvar('title', v.title)
            it.setvar('name', v.name)
            it.setvar('icon', icon)
            it.setvar('jsonpath', v.jsonpath)
            it.setvar('search_url', v.search_url)
            it.setvar('suggest_url', v.suggest_url)
            if v.pcencode:
                it.setvar('pcencode', '1')

        wf.send_feedback()

    return
