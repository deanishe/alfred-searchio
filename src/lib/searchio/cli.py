#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-13
#

"""Command-line interface to searchio command."""

from __future__ import print_function, absolute_import

import logging
import sys

log = logging.getLogger('workflow.{}'.format(__name__))


def cli(wf):
    """Script entry point.

    Args:
        wf (workflow.Workflow): Active workflow instance.
    """
    from docopt import docopt

    from searchio import DEFAULT_ENGINE, HELP_MAIN
    from searchio import core
    from searchio import util

    # Use system language as default variant
    lang = wf.cached_data('system-language',
                          lambda: util.get_system_language(),
                          max_age=86400)
    log.debug('default variant=%r, default=engine=%r', lang, DEFAULT_ENGINE)

    args = docopt(HELP_MAIN.format(variant=lang,
                                   engine=DEFAULT_ENGINE), wf.args)

    log.debug('args=%r', args)

    query = wf.decode(args.get('<query>') or '')
    engine_id = wf.decode(args.get('--engine') or '')
    variant = wf.decode(args.get('--variant') or '')

    # ---------------------------------------------------------
    # List engines

    if args.get('list'):
        return core.do_list_engines(wf, query)

    # ---------------------------------------------------------
    # List variants

    if args.get('variants'):
        return core.do_list_variants(wf, engine_id, query)

    # ---------------------------------------------------------
    # Perform search

    if args.get('search'):
        # Check for updates and notify user if one is available
        if (wf.update_available and
                wf.settings.get('show_update_notification', True)):
            wf.add_item(u'Update available',
                        u'↩ to install update',
                        autocomplete='workflow:update',
                        icon='icons/update-available.png')

        engine_id = engine_id or DEFAULT_ENGINE
        return core.do_search(wf, query, engine_id, variant)


def main():
    from workflow import Workflow3
    from searchio import UPDATE_SETTINGS, HELP_URL
    wf = Workflow3(update_settings=UPDATE_SETTINGS,
                   help_url=HELP_URL)
    sys.exit(wf.run(cli))
