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

from docopt import docopt
from workflow import web

from searchio import opensearch, util

log = util.logger(__name__)

wf = None


def usage(wf):
    """CLI usage instructions."""
    return __doc__


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
                suggest_url=search.suggest_url, jsonpath=search.jsonpath)

    return data, None


def run(wf, argv):
    """Run ``searchio web`` sub-command."""
    args = docopt(usage(wf), argv)
    error = search = None
    url = args.get('<url>')
    # Clear old cache data
    wf.clear_session_cache()

    search, error = import_search(wf, url)
    data = dict(error=error, search=search)
    wf.cache_data('import', data, session=True)
