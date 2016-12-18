#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-13
#

"""searchio <command> [<options>] [<args>...]

Alfred 3 workflow to provide search completion suggestions
from various search engines in various languages.

Usage:
    searchio <command> [<args>...]
    searchio -h|--version

Options:
    -h, --help       Display this help message
    --version        Show version number and exit

Commands:
    add          Add a new search to the workflow
    clean        Delete stale cache files
    config       Display (filtered) settings
    help         Show help for a command
    list         Display (filtered) list of engines
    reload       Update info.plist
    search       Perform a search
    variants     Display (filtered) list of engine variants
"""

from __future__ import print_function, absolute_import

import logging
import sys

log = logging.getLogger('workflow.{}'.format(__name__))


def usage(wf=None):
    """CLI usage instructions."""
    return __doc__


def cli(wf):
    """Script entry point.

    Args:
        wf (worflow.Workflow3): Active workflow object.

    """
    from docopt import docopt

    vstr = '{} v{}'.format(wf.name, wf.version)
    wf.args
    args = docopt(usage(wf), version=vstr, options_first=True)
    log.debug('args=%r', args)

    cmd = args.get('<command>')
    argv = [cmd] + args.get('<args>')

    # ---------------------------------------------------------
    # Call sub-command

    if cmd == 'add':
        from searchio.cmd.add import run
        return run(wf, argv)

    elif cmd == 'clean':
        from searchio.cmd.clean import run
        return run(wf, argv)

    elif cmd == 'config':
        from searchio.cmd.config import run
        return run(wf, argv)

    elif cmd == 'help':
        from searchio.cmd.help import run
        return run(wf, argv)

    elif cmd == 'list':
        from searchio.cmd.list import run
        return run(wf, argv)

    if cmd == 'reload':
        from searchio.cmd.reload import run
        return run(wf, argv)

    if cmd == 'search':
        from searchio.cmd.search import run
        return run(wf, argv)

    if cmd == 'user':
        from searchio.cmd.user import run
        return run(wf, argv)

    elif cmd == 'variants':
        from searchio.cmd.variants import run
        return run(wf, argv)

    else:
        raise ValueError('Unknown command "{}". Use -h for help.'.format(cmd))


def main():
    from workflow import Workflow3
    from searchio import UPDATE_SETTINGS, HELP_URL
    wf = Workflow3(update_settings=UPDATE_SETTINGS,
                   help_url=HELP_URL)
    sys.exit(wf.run(cli))
