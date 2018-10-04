#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-10
#

"""searchio toggle <setting>

Toggle a workflow setting on/off.

Usage:
    searchio toggle <setting>
    searchio toggle -h

Options:
    -h, --help   Display this help message

"""

from __future__ import print_function, absolute_import

from docopt import docopt
from workflow import Variables
from workflow.util import set_config

from searchio.core import Context
from searchio import util

log = util.logger(__name__)


def usage(wf):
    """CLI usage instructions."""
    return __doc__


def do_toggle_show_query(wf):
    """Toggle "show query in results" setting."""
    ctx = Context(wf)
    v = ctx.getbool('SHOW_QUERY_IN_RESULTS')
    if v:
        new = '0'
        status = 'off'
    else:
        new = '1'
        status = 'on'

    log.debug('turning "SHOW_QUERY_IN_RESULTS" %s ...', status)
    set_config('SHOW_QUERY_IN_RESULTS', new)

    print(Variables(title='Show query in results', text='Turned ' + status))


def do_toggle_alfred_sorts(wf):
    """Toggle "Alfred sorts results" setting."""
    ctx = Context(wf)
    v = ctx.getbool('ALFRED_SORTS_RESULTS')
    if v:
        new = '0'
        status = 'off'
    else:
        new = '1'
        status = 'on'

    log.debug('turning "ALFRED_SORTS_RESULTS" %s ...', status)
    set_config('ALFRED_SORTS_RESULTS', new)

    print(Variables(title='Alfred sorts results', text='Turned ' + status))


def run(wf, argv):
    """Run ``searchio web`` sub-command."""
    args = docopt(usage(wf), argv)
    key = args.get('<setting>')
    if key == 'show-query':
        return do_toggle_show_query(wf)
    if key == 'alfred-sorts':
        return do_toggle_alfred_sorts(wf)

    raise ValueError('Unknown Setting: ' + key)
