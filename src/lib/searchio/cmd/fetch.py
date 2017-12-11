#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-10
#

"""searchio fetch <url>

Import an OpenSearch websearch from a URL.

Usage:
    searchio fetch <url>
    searchio fetch -h

Options:
    -h, --help   Display this help message

"""

from __future__ import print_function, absolute_import

import json
from urlparse import urlparse

from docopt import docopt
from workflow import web

from searchio.core import Context
from searchio import opensearch, util

log = util.logger(__name__)

wf = None


def usage(wf):
    """CLI usage instructions."""
    return __doc__


# def do_import_search(wf, url):
#     """Parse URL for OpenSearch config."""
#     from workflow import web
#     from searchio import opensearch

#     ctx = Context(wf)
#     ICON_ERROR = ctx.icon('error')
#     ICON_IMPORT = ctx.icon('import')
#     error = None

#     if error:
#         wf.add_item(error, icon=ICON_ERROR)
#         wf.send_feedback()
#         return

#     icon = wf.workflowfile('icons/icon.png')
#     item_icon = ICON_IMPORT
#     if search.icon_url:
#         log.info('fetching search icon ...')
#         p = wf.datafile('icons/{}.png'.format(search.uid))
#         try:
#             r = web.get(search.icon_url)
#             r.raise_for_status()
#         except Exception as err:
#             log.error('error fetching icon (%s): %r', search.icon_url, err)
#         else:
#             r.save_to_path(p)
#             icon = p
#             item_icon = p

#     it = wf.add_item(u'Add "{}"'.format(search.name),
#                      u'↩ to add search',
#                      valid=True,
#                      icon=item_icon)

#     it.setvar('engine', 'OpenSearch')
#     it.setvar('uid', search.uid)
#     it.setvar('title', search.name)
#     it.setvar('name', search.name)
#     it.setvar('icon', icon)
#     # it.setvar('jsonpath', search.jsonpath)
#     it.setvar('search_url', search.search_url)
#     it.setvar('suggest_url', search.suggest_url)

#     wf.send_feedback()


def import_search(wf, url):
    """Fetch a search from URL."""
    log.info('[fetch] importing "%s" ...', url)
    error = search = None

    wf.cache_data('import-status', u'Fetching {}…'.format(url), session=True)
    try:
        search = opensearch.parse(url)
    except opensearch.NoAutoSuggest:
        error = 'Autosuggest is not supported'
    except opensearch.Invalid:
        error = "Couldn't parse OpenSearch definition"
    except opensearch.NotFound:
        error = "Site doesn't support OpenSearch"
    except Exception as err:
        error = str(err)

    if error:
        return None, error

    icon = wf.workflowfile('icon.png')
    if search.icon_url:
        log.info('[fetch] retrieving icon for "%s" ...', search.name)
        wf.cache_data('import-status',
                      u'Fetching icon for "{}"…'.format(search.name),
                      session=True)
        try:
            r = web.get(search.icon_url)
            r.raise_for_status()
        except Exception as err:
            log.error('[fetch] error fetching icon (%s): %r',
                      search.icon_url, err)
        else:
            p = wf.datafile('icons/{}.png'.format(search.uid))
            r.save_to_path(p)
            icon = p

    data = dict(engine="OpenSearch", uid=search.uid, title=search.name,
                name=search.name, icon=icon, search_url=search.search_url,
                suggest_url=search.suggest_url)

    return data, None


def run(wf, argv):
    """Run ``searchio web`` sub-command."""
    args = docopt(usage(wf), argv)
    error = search = None
    url = args.get('<url>')
    search, error = import_search(wf, url)
    data = dict(error=error, search=search)
    wf.cache_data('import', data, session=True)