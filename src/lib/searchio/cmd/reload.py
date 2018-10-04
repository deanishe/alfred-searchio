#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-17
#

"""searchio reload [-h]

Update info.plist from saved searches.

Usage:
    searchio reload [--defaults]
    searchio -h

Options:
    -d, --defaults  Use default searches, not user's.
    -h, --help      Display this help message.

"""

from __future__ import print_function, absolute_import

import json
import os
from plistlib import readPlist, readPlistFromString, writePlist

from docopt import docopt
from searchio.core import Context
from searchio.engines import Search
from searchio import util

log = util.logger(__name__)

# X position of all generated Script Filters
XPOS = 270
# Y position of first Script Filter
YPOS = 220
# Vertical space between (top of) each Script Filter
YOFFSET = 170

# UID of action to connect Script Filters to
OPEN_URL_UID = '1133DEAA-5A8F-4E7D-9E9C-A76CB82D9F92'

SCRIPT_FILTER = """
<dict>
    <key>config</key>
    <dict>
        <key>alfredfiltersresults</key>
        <false/>
        <key>alfredfiltersresultsmatchmode</key>
        <integer>0</integer>
        <key>argumenttrimmode</key>
        <integer>0</integer>
        <key>argumenttype</key>
        <integer>0</integer>
        <key>escaping</key>
        <integer>102</integer>
        <key>keyword</key>
        <string>g</string>
        <key>queuedelaycustom</key>
        <integer>3</integer>
        <key>queuedelayimmediatelyinitially</key>
        <false/>
        <key>queuedelaymode</key>
        <integer>0</integer>
        <key>queuemode</key>
        <integer>2</integer>
        <key>runningsubtext</key>
        <string>Fetching results…</string>
        <key>script</key>
        <string>./searchio search google-en "$1"</string>
        <key>scriptargtype</key>
        <integer>1</integer>
        <key>scriptfile</key>
        <string></string>
        <key>subtext</key>
        <string>Searchio!</string>
        <key>title</key>
        <string>Google Search (English)</string>
        <key>type</key>
        <integer>0</integer>
        <key>withspace</key>
        <true/>
    </dict>
    <key>type</key>
    <string>alfred.workflow.input.scriptfilter</string>
    <key>uid</key>
    <string>18E144DF-1054-4A12-B5F0-AC05C6F7DEFD</string>
    <key>version</key>
    <integer>2</integer>
</dict>
"""

# Default search engines
DEFAULTS = [
    {
        'title': 'Google (English)',
        'icon': 'icons/engines/google.png',
        'jsonpath': '$[1][*]',
        'keyword': 'g',
        'search_url': 'https://www.google.com/search?q={query}&hl=en&safe=off',
        'suggest_url': 'https://suggestqueries.google.com/complete/search?client=firefox&q={query}&hl=en',
        'uid': 'google-en',
    },
    {
        'title': 'Google (Deutsch)',
        'icon': 'icons/engines/google.png',
        'jsonpath': '$[1][*]',
        'keyword': 'gd',
        'search_url': 'https://www.google.com/search?q={query}&hl=de&safe=off',
        'suggest_url': 'https://suggestqueries.google.com/complete/search?client=firefox&q={query}&hl=de',
        'uid': 'google-de',
    },
    {
        'title': 'Wikipedia (English)',
        'icon': 'icons/engines/wikipedia.png',
        'jsonpath': '$[1][*]',
        'pcencode': True,
        'keyword': 'w',
        'search_url': 'https://en.wikipedia.org/wiki/{query}',
        'suggest_url': 'https://en.wikipedia.org/w/api.php?action=opensearch&search={query}',
        'uid': 'wikipedia-en',
    },
    {
        'title': 'Wikipedia (Deutsch)',
        'icon': 'icons/engines/wikipedia.png',
        'jsonpath': '$[1][*]',
        'pcencode': True,
        'keyword': 'wd',
        'search_url': 'https://de.wikipedia.org/wiki/{query}',
        'suggest_url': 'https://de.wikipedia.org/w/api.php?action=opensearch&search={query}',
        'uid': 'wikipedia-de',
    },
    {
        'title': 'YouTube (United States)',
        'icon': 'icons/engines/youtube.png',
        'jsonpath': '$[1][*]',
        'keyword': 'yt',
        'search_url': 'https://www.youtube.com/results?gl=us&persist_gl=1&search_query={query}',
        'suggest_url': 'https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=us&q={query}',
        'uid': 'youtube-us',
    },
    {
        'title': 'YouTube (Germany)',
        'icon': 'icons/engines/youtube.png',
        'jsonpath': '$[1][*]',
        'keyword': 'ytd',
        'search_url': 'https://www.youtube.com/results?gl=de&persist_gl=1&search_query={query}',
        'suggest_url': 'https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=de&q={query}',
        'uid': 'youtube-de',
    },
]


def usage(wf=None):
    """CLI usage instructions."""
    return __doc__


def remove_script_filters(wf, data):
    """Remove auto-generated Script Filters from info.plist data."""
    ids = set()
    for k, d in data['uidata'].items():
        if 'colorindex' not in d:
            ids.add(k)

    keep = []
    delete = []

    for obj in data['objects']:
        if obj['uid'] in ids and \
                obj['type'] == 'alfred.workflow.input.scriptfilter':
            log.info('Removed Script Filter "%s" (%s)',
                     obj['config']['title'], obj['uid'])
            delete.append(obj['uid'])
            continue
        keep.append(obj)

    data['objects'] = keep

    # Remove connections and uidata
    for uid in delete:
        del data['connections'][uid]
        del data['uidata'][uid]


def add_script_filters(wf, data, searches=None):
    """Add user searches to info.plist data."""
    ctx = Context(wf)
    only = set()

    if searches:  # add them to the user's searches dir
        for s in searches:
            path = os.path.join(ctx.searches_dir, s.uid + '.json')
            with open(path, 'wb') as fp:
                json.dump(s.dict, fp)
            only.add(s.uid)
            log.info('Saved search "%s"', s.title)

    f = util.FileFinder([ctx.searches_dir], ['json'])
    searches = [Search.from_file(p) for p in f]
    if only:
        searches = [s for s in searches if s.uid in only]

    searches.sort(key=lambda s: s.title)

    ypos = YPOS
    for s in searches:
        if not s.keyword:
            log.error('No keyword for search "%s" (%s)', s.title, s.uid)
            continue

        d = readPlistFromString(SCRIPT_FILTER)
        d['uid'] = s.uid
        d['config']['title'] = s.title
        # d['config']['script'] = './searchio search {} "$1"'.format(s.uid)
        d['config']['script'] = './search {} "$1"'.format(s.uid)
        d['config']['keyword'] = s.keyword
        data['objects'].append(d)
        data['connections'][s.uid] = [{
            'destinationuid': OPEN_URL_UID,
            'modifiers': 0,
            'modifiersubtext': '',
            'vitoclose': False,
        }]
        data['uidata'][s.uid] = {
            'note': s.title,
            'xpos': XPOS,
            'ypos': ypos,
        }
        ypos += YOFFSET
        log.info('Added Script Filter "%s" (%s)', s.title, s.uid)

    link_icons(wf, searches)


def link_icons(wf, searches):
    """Create symlinks for Script Filter icons."""
    # Remove existing icon symlinks
    for fn in os.listdir(wf.workflowdir):
        if not fn.endswith('.png'):
            continue
        p = wf.workflowfile(fn)
        if not os.path.islink(p):
            continue

        os.unlink(p)
        log.debug('Removed search icon "%s"', p)

    for s in searches:
        src = s.icon
        dest = wf.workflowfile(s.uid + '.png')
        if os.path.exists(dest):
            continue

        src = os.path.relpath(src, wf.workflowdir)
        dest = os.path.relpath(dest, wf.workflowdir)
        log.debug('Linking "%s" to "%s"', src, dest)
        os.symlink(src, dest)


def run(wf, argv):
    """Run ``searchio reload`` sub-command."""
    args = docopt(usage(wf), argv)
    searches = None
    log.debug('args=%r', args)

    if args['--defaults']:
        searches = [Search.from_dict(d) for d in DEFAULTS]

    ip = wf.workflowfile('info.plist')
    data = readPlist(ip)

    remove_script_filters(wf, data)
    add_script_filters(wf, data, searches)
    writePlist(data, ip)
