#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-17
#

"""searchio list [-t] [<query>]

Display (and optionally filter) list of installed
suggestion engines.

Usage:
    searchio list [-t] [<query>]
    searchio list -h

Options:
    -t, --text     Print results as text, not Alfred JSON
    -h, --help     Display this help message
"""

from __future__ import print_function, absolute_import

from operator import attrgetter
import sys

from docopt import docopt

from searchio.core import Context
from searchio import engines
# from searchio.engines import load as load_engines
from searchio import util

log = util.logger(__name__)

_text_help = """\
searchio supports the following search engines.

To view an engine's variants, use:
    searchio variants <ID> ...

"""


def usage(wf=None):
    """CLI usage instructions."""
    return __doc__


def run(wf, argv):
    """Run ``searchio list`` sub-command."""
    args = docopt(usage(wf), argv)
    ctx = Context(wf)
    query = wf.decode(args.get('<query>') or '').strip()
    ICON_BACK = ctx.icon('back')

    engs = engines.load(*ctx.engine_dirs)
    # engs = engines.engines()

    if query:
        engs = wf.filter(query, engs, key=attrgetter('title'))
    else:
        it = wf.add_item(
            u'Configuration',
            'Back to configuration',
            arg='back',
            valid=True,
            icon=ICON_BACK)
        it.setvar('action', 'back')

    if args.get('--text') or util.textmode():  # Display for terminal

        print(_text_help, file=sys.stderr)

        table = util.Table([u'ID', u'Name', u'Description', u'Variants'])
        for e in engs:
            n = '{:>8}'.format(len(e.variants))
            table.add_row((e.uid, e.title, e.description, n))

        print(table)
        print()

    else:  # Display for Alfred
        for e in engs:
            title = u'{} …'.format(e.title)
            subtitle = (str(len(e.variants)) + ' variant' +
                        ('s', '')[len(e.variants) == 1])
            it = wf.add_item(
                title,
                subtitle,
                autocomplete=e.title,
                arg=e.uid,
                valid=True,
                icon=ctx.icon(e.uid))
            it.setvar('engine', e.uid)
            it.setvar('action', 'searches')

        wf.send_feedback()
