#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-17
#

"""searchio search [options] <search> <query>

Ask specified engine for suggestions for <query>.
<search> should be the UID of a search.

Usage:
    searchio search [-t] <search> <query>
    searchio search -h

<search> may be a path or a UID.

Options:
    -t, --text     Print results as text, not Alfred JSON
    -h, --help     Display this help message
"""

from __future__ import print_function, absolute_import

from collections import namedtuple
import hashlib
import os
import sys
from time import time

from docopt import docopt

from searchio import MAX_CACHE_AGE
from searchio import engines
from searchio.core import Context
from searchio import util

log = util.logger(__name__)


Result = namedtuple('Result', 'term url source')


def usage(wf):
    """CLI usage instructions."""
    return __doc__


def cached_search(ctx, search, query):
    """Perform a cache-backed search.

    Cached entries are expired after ``MAX_CACHE_AGE`` seconds.

    Args:
        ctx (core.Context): Current context
        search (searchio.engines.Search): Search configuration
        query (unicode): Search query to return suggestions for

    Returns:
        list: Search suggestions. Sequence of Unicode strings.

    No Longer Raises:
        ValueError: Raised if search is unknown

    """
    if not search.suggest_url:
        log.debug('[search/%s] Suggestions not supported', search.uid)
        return []

    url = util.mkurl(search.suggest_url, query, search.pcencode)

    # Caching configuration
    h = hashlib.md5(query.encode('utf-8')).hexdigest()
    reldir = 'searches/{}/{}/{}'.format(search.uid, h[:2], h[2:4])
    # Ensure cache directory exists
    dirpath = os.path.join(ctx.wf.cachedir, reldir)
    try:
        os.makedirs(dirpath)
    except OSError as err:
        if err.errno != 17:
            raise err

    key = u'{}/{}'.format(reldir, h)

    def _search():
        """Fetch and parse JSON response."""
        from jsonpath_rw import parse
        # results = OrderedDict()
        results = []
        urls = set()  # URLs to results

        # result based on user's query
        qr = Result(query,
                    util.mkurl(search.search_url, query, search.pcencode),
                    search.title)

        data = util.getjson(url)

        # parse JSONPath and unwrap results
        jx = parse(search.jsonpath)

        terms = []
        for m in jx.find(data):
            v = m.value
            if isinstance(v, unicode):
                terms.append(v)
            elif isinstance(v, list):
                terms.extend(v)

        for term in terms:
            r = Result(term,
                       util.mkurl(search.search_url, term, search.pcencode),
                       search.title)
            results.append(r)
            urls.add(r.url)

        # add query-based result at the end if it's not a duplicate
        if qr.url not in urls:
            results.append(qr)

        return results

    return ctx.wf.cached_data(key, _search, max_age=MAX_CACHE_AGE)


def run(wf, argv):
    """Run ``searchio search`` sub-command."""
    args = docopt(usage(wf), argv)
    ctx = Context(wf)
    query = wf.decode(args.get('<query>') or '').strip()
    uid = wf.decode(args.get('<search>') or '').strip()
    if not uid or not query:
        raise RuntimeError('<search> and <query> are required')

    start = time()
    p = ctx.search(uid)
    if not os.path.exists(p):
        raise ValueError('Unknown search "{}" ({!r})'.format(uid, p))

    search = engines.Search.from_file(p)

    results = cached_search(ctx, search, query)

    log.debug('[search/%s] %d result(s) in %0.3fs',
              uid, len(results), time() - start)

    # ---------------------------------------------------------
    # Text results

    if args.get('--text') or util.textmode():
        print()
        msg = u'{:d} result(s) for "{:s}"'.format(len(results), query)
        print(msg, file=sys.stderr)
        print('=' * len(msg))
        print()
        table = util.Table([u'Suggestion', u'URL'])
        for r in results:
            table.add_row(r[:2])
            # print('{0}\t{1}'.format(term, url))
        print(table)
        print()

    # ---------------------------------------------------------
    # Alfred results

    else:
        for r in results:
            wf.add_item(
                r.term,
                u'Search {} for "{}"'.format(r.source, r.term),
                arg=r.url,
                autocomplete=r.term + u' ',
                valid=True,
                icon=search.icon,
            )

        wf.send_feedback()
