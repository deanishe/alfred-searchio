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
core.py
=======

User-facing workflow functions.
"""

from __future__ import print_function, absolute_import

from hashlib import md5
import logging
import os
import sys

from workflow import ICON_SETTINGS

from searchio import HELP_LIST, HELP_VARIANTS, MAX_CACHE_AGE
from searchio.engines import Manager as EngineManager
from searchio import util


log = logging.getLogger('workflow.{}'.format(__name__))


def cached_search(wf, engine, variant_id, query):

    h = md5(query.encode('utf-8')).hexdigest()
    reldir = 'searches/{}/{}/{}/{}'.format(engine.id, variant_id,
                                           h[:2], h[2:4])
    # Ensure cache directory exists
    dirpath = wf.cachefile(reldir)
    # log.debug('reldir=%r, dirpath=%r', reldir, dirpath)
    # log.debug('bundleid=%r', wf.bundleid)
    # log.debug('info=%r', wf.info)
    # log.debug('env=%r', wf.alfred_env)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    key = u'{0}/{1}'.format(reldir, h)

    def _wrapper():
        return engine.suggest(query, variant_id)

    return wf.cached_data(key, _wrapper, max_age=MAX_CACHE_AGE)


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
    engine_dirs = [os.path.join(os.path.dirname(__file__), 'engines')]
    em = EngineManager(engine_dirs)

    engine = em.get_engine(engine_id)
    if not engine:
        raise ValueError('Unknown engine : {0!r}'.format(engine_id))

    if variant_id not in engine.variants:
        if '*' in engine.variants:
            variant_id = '*'
        else:
            raise ValueError('Unknown variant for {0!r} : {1!r}'.format(
                engine.name, variant_id))

    variant = engine.variants[variant_id]

    qir = (u'No', u'Yes')[wf.settings.get('show_query_in_results',
                                          False)]

    # TODO: Cache search results
    # results = engine.suggest(query, variant_id)
    results = cached_search(wf, engine, variant_id, query)

    if wf.settings.get('show_query_in_results'):
        results = [query] + results

    log.debug('results=%r', results)

    # ---------------------------------------------------------
    # Text results

    if util.textmode():
        print()
        msg = u'{0:d} results for "{1:s}"'.format(len(results), query)
        print(msg, file=sys.stderr)
        print('=' * len(msg))
        print()
        # TODO: Show URLs in text search results?
        table = util.Table([u'Suggestion', u'URL'])
        for term in results:
            url = engine.get_search_url(term, variant_id)
            table.add_row((term, url))
            # print('{0}\t{1}'.format(term, url))
        print(table)
        print()

    # ---------------------------------------------------------
    # XML results

    else:  # XML results for Alfred
        def subtitle(term):
            return u'Search {} ({}) for "{}"'.format(engine.name,
                                                     variant['name'],
                                                     term)

        for term in results:
            url = engine.get_search_url(term, variant_id)
            wf.add_item(term,
                        subtitle(term),
                        arg=url,
                        # uid=url,
                        autocomplete=term + u' ',
                        valid=True,
                        icon=engine.icon)

        # Show `query` in results if that option is set and query
        # isn't already in `results`. Use `query` as fallback if
        # there are no results.
        if query not in results:
            url = engine.get_search_url(query, variant_id)
            wf.add_item(query,
                        subtitle(query),
                        arg=url,
                        # uid=url,
                        autocomplete=query + u' ',
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
        raise ValueError('Unknown engine : {!r}'.format(engine_id))

    log.debug('engine=%r', engine)
    var = engine.variants
    variants = [(vid, var[vid]['name']) for vid in var]

    if query:
        variants = wf.filter(query, variants, lambda t: t[1].lower())
    else:
        variants.sort()

    # ---------------------------------------------------------
    # Show results

    if util.textmode():  # Display for terminal

        h = HELP_VARIANTS.format(name=engine.name,
                                 underline=(u'=' * len(engine.name)))
        print(h, file=sys.stderr)

        table = util.Table([u'ID', u'Variant'])
        for t in variants:
            table.add_row(t)
        print(table)
        print()

    else:  # Display for Alfred
        for name, vid in variants:
            wf.add_item(name,
                        u'{0} > {1}'.format(engine.id, vid),
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

    if util.textmode():  # Display for terminal

        print(HELP_LIST, file=sys.stderr)

        table = util.Table([u'ID', u'Search Engine'])
        for e in engines:
            table.add_row((e.id, e.name))

        print(table)
        print()

    else:  # Display for Alfred
        # Show settings
        # TODO: Move settings to a separate command
        qir = (u'No', u'Yes')[wf.settings.get('show_query_in_results',
                                              False)]
        wf.add_item(u'Show query in results: {}'.format(qir),
                    u'Action this item to toggle setting',
                    arg='toggle-query-in-results',
                    valid=True,
                    icon=ICON_SETTINGS)

        qir = (u'No', u'Yes')[wf.settings.get('show_update_notification',
                                              True)]
        wf.add_item(u'Notify of new versions: {}'.format(qir),
                    u'Action this item to toggle setting',
                    arg='toggle-update-notification',
                    valid=True,
                    icon=ICON_SETTINGS)

        # Show engines
        # TODO: Repair listing engines in Alfred
        for engine in engines:
            subtitle = (u'Use `./searchio --engine {} "…"` '
                        u'in your Script Filter'.format(engine.id))
            wf.add_item(
                engine.name,
                subtitle,
                valid=False,
                icon=engine.icon)
        wf.send_feedback()
    return
