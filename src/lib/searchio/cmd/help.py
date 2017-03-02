#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-17
#

"""searchio help [options] [<command>]

Display help message for command(s).

Usage:
    searchio help [<command>]
    searchio help --online
    searchio help -h

Options:
    --online       Open online help in browser
    -h, --help     Display this help message
"""

from __future__ import print_function, absolute_import

# from operator import itemgetter

from docopt import docopt
from searchio import util

log = util.logger(__name__)


def usage(wf=None):
    """CLI usage instructions."""
    return __doc__


def run(wf, argv):
    """Run ``searchio list`` sub-command."""
    # Use system language as default variant
    # df = get_defaults(wf)
    import searchio.cli
    import searchio.cmd.add
    import searchio.cmd.clean
    import searchio.cmd.config
    import searchio.cmd.list
    import searchio.cmd.reload
    import searchio.cmd.search
    import searchio.cmd.user
    import searchio.cmd.variants

    commands = {
        'add': searchio.cmd.add.usage,
        'clean': searchio.cmd.clean.usage,
        'config': searchio.cmd.config.usage,
        'help': usage,
        'list': searchio.cmd.list.usage,
        'reload': searchio.cmd.reload.usage,
        'search': searchio.cmd.search.usage,
        'user': searchio.cmd.user.usage,
        'variants': searchio.cmd.variants.usage,
    }

    args = docopt(usage(wf), argv)

    log.debug('args=%r', args)

    if args.get('--online'):
        return wf.open_help()

    cmd = wf.decode(args.get('<command>') or '').strip()
    if not cmd:
        print(searchio.cli.usage(wf))
        return
    elif cmd not in commands:
        raise ValueError('Unknown command: {!r}'.format(cmd))
    print(commands[cmd](wf))
