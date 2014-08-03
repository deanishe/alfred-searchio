#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-03
#

"""settings.py <command>

Usage:
    settings.py
    settings.py toggle-query-in-results

Options:
    toggle-query-in-results    Whether to show <query> in results or not
    -h, --help                 Show this message
"""

from __future__ import print_function, unicode_literals

import sys
import subprocess

from workflow import Workflow

log = None

ALFRED_SCRIPT = 'tell application "Alfred 2" to search "{}"'


def _applescriptify(text):
    """Replace double quotes in text"""
    return text.replace('"', '" + quote + "')


def call_alfred(query):
    """Run Alfred with ``query`` via AppleScript"""
    script = ALFRED_SCRIPT.format(_applescriptify(query))
    log.debug('calling Alfred with : {!r}'.format(script))
    return subprocess.call(['osascript', '-e', script])


def main(wf):
    from docopt import docopt
    args = docopt(__doc__, wf.args)
    log.debug('args : {}'.format(args))

    if args.get('toggle-query-in-results'):
        qir = not wf.settings.get('show_query_in_results', False)
        wf.settings['show_query_in_results'] = qir
        if qir:
            print('Query will be shown in suggestions')
        else:
            print('Query will not be shown in suggestions')

        return call_alfred('searchio')

    # Default: show settings.
    # qir = ('No', 'Yes')[wf.settings.get('show_query_in_results', False)]
    # wf.add_item('Show query in results: {}'.format(qir),
    #             'Action this item to toggle setting',
    #             arg='show_query_in_results',
    #             valid=True,
    #             icon=ICON_SETTINGS)
    # wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
