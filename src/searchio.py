#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-05-11
#

"""
searchio.py
===========
"""

from __future__ import print_function, unicode_literals

import os
import sys
import subprocess

from workflow import Workflow, ICON_SETTINGS

from engines import get_engines
from engines import Manager as EngineManager
import util


DEFAULT_ENGINE = 'google'

UPDATE_SETTINGS = {'github_slug': 'deanishe/alfred-searchio'}
HELP_URL = 'https://github.com/deanishe/alfred-searchio/issues'

# dP     dP           dP
# 88     88           88
# 88aaaaa88a .d8888b. 88 88d888b.
# 88     88  88ooood8 88 88'  `88
# 88     88  88.  ... 88 88.  .88
# dP     dP  `88888P' dP 88Y888P'
#                        88
#                        dP

HELP_MAIN = """\
searchio.py [<command>] [options] [<query>]

Provide auto-suggestion results for <query>.

<engine> is the ID (short name). View them all with:
    searchio.py list

Use `list` and `variants` to view the available engines/variants.


Usage:
    searchio.py search [-e <engine>] [-v <variant>] <query>
    searchio.py settings [<query>]
    searchio.py list [<query>]
    searchio.py variants [-e <engine>] [<query>]
    searchio.py -h

Options:
    -e, --engine=<ID>       ID (short name) of search engine to use
                            [default: {engine}]
    -v, --variant=<ID>      ID (short name) of variant to use
                            [default: {variant}]
    -t, --text              Print results as text, not Alfred XML
    -h, --help              Display this help message
"""


HELP_LIST = """
Searchio! supported engines
===========================

Use `ID` to specify the engine to `searchio.py search`, e.g. to search
DuckDuckGo for "socks".

    searchio.py search ddg socks

Use `searchio.py variants -e <engine>` to see an engine's variants.
"""

HELP_VARIANTS = """
Variants for {name}
============={underline}

Use `-v <ID>` to specify a variant, e.g. to search Amazon Germany:

    searchio.py search -e amazon -v de socken
"""

# dP     dP           dP
# 88     88           88
# 88aaaaa88a .d8888b. 88 88d888b. .d8888b. 88d888b. .d8888b.
# 88     88  88ooood8 88 88'  `88 88ooood8 88'  `88 Y8ooooo.
# 88     88  88.  ... 88 88.  .88 88.  ... 88             88
# dP     dP  `88888P' dP 88Y888P' `88888P' dP       `88888P'
#                        88
#                        dP

log = None


class CommandError(Exception):
    """Improved exception for exec'd commands.

    Raised by `check_output()` if a command exits with non-zero status.

    Attributes:
        command (list): Command that was run.
        returncode (int): Exit status of command.
        stderr (str): Command's STDERR output.
    """

    def __init__(self, command, returncode, stderr):
        """Create new `CommandError`.

        Args:
            command (sequence): The first argument passed to `subprocess.Popen()`.
            returncode (int): The exit code of the process.
            stderr (str): The output on STDERR of the process.
        """
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        super(CommandError, self).__init__(command, returncode, stderr)

    def __str__(self):
        """Prettified error message.

        Returns:
            unicode: Error message.
        """
        return 'CommandError: {!r} exited with {!r}:\n{}'.format(
            self.command, self.returncode, self.stderr)

    def __repr__(self):
        """Code-like representation of the error.

        Returns:
            unicode: String representation of error.
        """
        return 'CommandError({!r}, {!r}, {!r})'.format(
            self.command, self.returncode, self.stderr)


def check_output(cmd):
    """Run `cmd` with `subprocess` and capture output.

    Args:
        cmd (list): Command to execute (first argument to
            `subprocess.Popen()`).

    Raises:
        CommandError: Raised if command exists with non-zero status.

    Returns:
        str: Output of command (STDOUT).
    """
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    stdout, stderr = proc.communicate()
    if proc.returncode:
        raise CommandError(cmd, proc.returncode, stderr)

    return stdout


def get_system_language():
    """Return system language.

    Defaults to `'en'` if `AppleLanguages` is not set.

    Returns:
        str: Language name, e.g. 'en', 'de'.
    """
    try:
        output = check_output(['defaults', 'read', '-g', 'AppleLanguages'])
    except CommandError as err:
        log.error('Error reading AppleLanguages, defaulting to English:\n%s',
                  err)
        return 'en'

    output = output.strip('()\n ')
    langs = [s.strip('", ') for s in output.split('\n')]
    if not len(langs):
        raise ValueError('Could not determine system language')
    lang = langs[0]
    if len(lang) > 2:
        lang = lang[:2]
    log.debug('System language : %r', lang)
    return lang

# def get_engines():
#     engines = {}
#     for cls in Suggest.__subclasses__():
#         log.debug('subclass : {0}'.format(cls.name))
#         engines[cls.id_] = cls
#     return engines


def textmode():
    """Return `True` if STDOUT is a tty.

    Returns:
        bool: Whether STDOUT is a tty.
    """
    return sys.stdout.isatty()


# .d88888b                                      dP
# 88.    "'                                     88
# `Y88888b. .d8888b. .d8888b. 88d888b. .d8888b. 88d888b.
#       `8b 88ooood8 88'  `88 88'  `88 88'  `"" 88'  `88
# d8'   .8P 88.  ... 88.  .88 88       88.  ... 88    88
#  Y88888P  `88888P' `88888P8 dP       `88888P' dP    dP

def do_search(wf, query, engine_id, variant_id):
    """Display search results from specified engine and variant.

    Args:
        wf (workflow.Workflow): Active `Workflow` object.
        query (unicode): What to search for.
        engine_id (str): ID of search engine to use, e.g. `google`.
        variant_id (str): ID of engine variant, e.g. `en`, `de`.

    Raises:
        ValueError: Raised if an engine or variant is unknown.
    """
    log.debug('engine_id=%r, variant=%r', engine_id, variant_id)
    engines = get_engines()
    for engine in engines:
        if engine.id == engine_id:
            break
        else:
            raise ValueError('Unknown engine : {0!r}'.format(engine_id))

    if variant_id not in engine.variants:
        raise ValueError('Unknown variant for {0!r} : {1!r}'.format(
            engine.name, variant_id))

    variant = engine.variants[variant_id]
    qir = ('No', 'Yes')[wf.settings.get('show_query_in_results',
                                        False)]

    # TODO: Cache search results
    results = engine.suggest(query, variant_id)
    log.debug('results=%r', results)

    # ---------------------------------------------------------
    # Text results

    if textmode():
        print('{0:d} results for "{1:s}"'.format(len(results), query),
              file=sys.stderr)
        # TODO: Show URLs in text search results?
        for term in results:
            url = engine.get_search_url(term, variant_id)
            print('{0}\t{1}'.format(term, url))

    # ---------------------------------------------------------
    # XML results

    else:  # XML results for Alfred
        def subtitle(term):
            return 'Search {0} ({1}) for "{2}"'.format(engine.name,
                                                       variant['name'],
                                                       term)

        # Show `query` in results if that option is set and query
        # isn't already in `results`. Use `query` as fallback if
        # there are no results.
        if (qir or not results) and query not in results:
            url = engine.get_search_url(query, variant_id)
            wf.add_item(query,
                        subtitle(query),
                        arg=url,
                        uid=url,
                        autocomplete=query + ' ',
                        valid=True,
                        icon=engine.icon)

        for term in results:
            url = engine.get_search_url(term, variant_id)
            wf.add_item(term,
                        subtitle(term),
                        arg=url,
                        uid=url,
                        autocomplete=term + ' ',
                        valid=True,
                        icon=engine.icon)
        wf.send_feedback()


# .d88888b             dP     dP   oo
# 88.    "'            88     88
# `Y88888b. .d8888b. d8888P d8888P dP 88d888b. .d8888b. .d8888b.
#       `8b 88ooood8   88     88   88 88'  `88 88'  `88 Y8ooooo.
# d8'   .8P 88.  ...   88     88   88 88    88 88.  .88       88
#  Y88888P  `88888P'   dP     dP   dP dP    dP `8888P88 `88888P'
#                                                   .88
#                                               d8888P

def do_settings(wf, query=None):
    # TODO: Implement `do_settings()`
    pass


# dP     dP                   oo                     dP
# 88     88                                          88
# 88    .8P .d8888b. 88d888b. dP .d8888b. 88d888b. d8888P .d8888b.
# 88    d8' 88'  `88 88'  `88 88 88'  `88 88'  `88   88   Y8ooooo.
# 88  .d8P  88.  .88 88       88 88.  .88 88    88   88         88
# 888888'   `88888P8 dP       dP `88888P8 dP    dP   dP   `88888P'

def do_list_variants(wf, engine_id, query=None):
    engine_dirs = [os.path.join(os.path.dirname(__file__), 'engines')]
    em = EngineManager(engine_dirs)

    engine = em.get_engine(engine_id)

    if not engine:
        raise ValueError('Unknown engine : {0!r}'.format(engine_id))

    log.debug('engine=%r', engine)
    var = engine.variants
    variants = [(vid, var[vid]['name']) for vid in var]

    if query:
        variants = wf.filter(query, variants, lambda t: t[1].lower())
    else:
        variants.sort()

    # ---------------------------------------------------------
    # Show results

    if textmode():  # Display for terminal

        h = HELP_VARIANTS.format(name=engine.name,
                                 underline=('=' * len(engine.name)))
        print(h, file=sys.stderr)

        table = util.Table(['ID', 'Variant'])
        for t in variants:
            table.add_row(t)
        print(table)
        print()

    else:  # Display for Alfred
        for name, vid in variants:
            wf.add_item(name,
                        '{0} > {1}'.format(engine.id, vid),
                        icon=engine.icon)
        wf.send_feedback()


#  88888888b                   oo
#  88
# a88aaaa    88d888b. .d8888b. dP 88d888b. .d8888b. .d8888b.
#  88        88'  `88 88'  `88 88 88'  `88 88ooood8 Y8ooooo.
#  88        88    88 88.  .88 88 88    88 88.  ...       88
#  88888888P dP    dP `8888P88 dP dP    dP `88888P' `88888P'
#                          .88
#                      d8888P

def do_list_engines(wf, query):
    """Display a list of search engines filtered by `query`.

    Args:
        wf (workflow.Workflow): Active `Workflow` object.
        query (unicode): String to filter engines by. May be `None`
            or empty string.
    """
    engine_dirs = [os.path.join(os.path.dirname(__file__), 'engines')]
    em = EngineManager(engine_dirs)
    engines = em.engines

    if query:
        engines = wf.filter(query, engines, lambda e: e.name)

    if textmode():  # Display for terminal

        print(HELP_LIST, file=sys.stderr)

        table = util.Table(['ID', 'Search Engine'])
        for e in engines:
            table.add_row((e.id, e.name))

        print(table)
        print()

    else:  # Display for Alfred
        # Show settings
        # TODO: Move settings to a separate command
        qir = ('No', 'Yes')[wf.settings.get('show_query_in_results',
                                            False)]
        wf.add_item('Show query in results: {0}'.format(qir),
                    'Action this item to toggle setting',
                    arg='toggle-query-in-results',
                    valid=True,
                    icon=ICON_SETTINGS)

        qir = ('No', 'Yes')[wf.settings.get('show_update_notification',
                                            True)]
        wf.add_item('Notify of new versions: {0}'.format(qir),
                    'Action this item to toggle setting',
                    arg='toggle-update-notification',
                    valid=True,
                    icon=ICON_SETTINGS)

        # Show engines
        # TODO: Repair listing engines in Alfred
        for name, id_ in name_id_list:
            subtitle = ('Use `searchio.py {0} "{{query}}"` '
                        'in your Script Filter'.format(id_))
            wf.add_item(
                name,
                subtitle,
                valid=False,
                icon='icons/{0}.png'.format(id_))
        wf.send_feedback()
    return


#                     oo
#
# 88d8b.d8b. .d8888b. dP 88d888b.
# 88'`88'`88 88'  `88 88 88'  `88
# 88  88  88 88.  .88 88 88    88
# dP  dP  dP `88888P8 dP dP    dP

def main(wf):
    """Script entry point.

    Args:
        wf (workflow.Workflow): Active workflow instance.
    """
    from docopt import docopt

    # Use system language as default variant
    lang = wf.cached_data('system-language',
                          lambda: get_system_language(),
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
        return do_list_engines(wf, query)

    # ---------------------------------------------------------
    # List variants

    if args.get('variants'):
        return do_list_variants(wf, engine_id, query)

    # ---------------------------------------------------------
    # Perform search

    if args.get('search'):
        # Check for updates and notify user if one is available
        if (wf.update_available and
                wf.settings.get('show_update_notification', True)):
            wf.add_item('Update available',
                        '↩ to install update',
                        autocomplete='workflow:update',
                        icon='icons/update-available.png')

        engine_id = engine_id or DEFAULT_ENGINE
        return do_search(wf, query, engine_id, variant)


if __name__ == '__main__':
    wf = Workflow(update_settings=UPDATE_SETTINGS,
                  help_url=HELP_URL)
    log = wf.logger
    sys.exit(wf.run(main))
