#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-10
#

"""searchio web [<url>]

Import an OpenSearch websearch from a URL.

Usage:
    searchio web [<url>]
    searchio web -h

Options:
    -h, --help   Display this help message

"""

from __future__ import print_function, absolute_import

import json
import subprocess
from urlparse import urlparse

from docopt import docopt
from workflow import ICON_WARNING

from searchio.core import Context
from searchio import util

log = util.logger(__name__)

wf = None

# JXA script to test whether specified apps are running.
# App names are passed in ARGV; returns a {name: bool} JSON object.
JXA_RUNNING = """
function run(argv) {
    var apps = {};
    argv.forEach(function(name) {
        if (Application(name).running()) {
            apps[name] = true;
        } else {
            apps[name] = false;
        }
    });
    return JSON.stringify(apps);
}
"""

# JXA script for Safari-like browsers to get title and URL of current
# tab. Returns a JSON object.
JXA_SAFARI = """
function run(argv) {
    var doc = Application('%(appname)s').documents[0];

    return JSON.stringify({
        title: doc.name(),
        url: doc.url()
    });
}
"""

# JXA script for Chrome-like browsers to get title and URL of current
# tab. Returns a JSON object.
JXA_CHROME = """
function run(argv) {
    var tab = Application('%(appname)s').windows[0].activeTab;

    return JSON.stringify({
        title: tab.name(),
        url: tab.url()
    });
}
"""

BROWSERS = {
    # app name: (app path, JXA script)
    'Safari': ('/Applications/Safari.app', JXA_SAFARI),
    'Google Chrome': ('/Applications/Google Chrome.app', JXA_CHROME),
}


def usage(wf):
    """CLI usage instructions."""
    return __doc__


def clipboard_url():
    """Fetch URL from clipboard."""
    cmd = ['pbpaste', '-Prefer', 'txt']
    output = subprocess.check_output(cmd)

    url = urlparse(output)
    if url.scheme not in ('http', 'https'):
        return None

    return output.decode('utf-8')


def do_get_url(wf, args):
    """Check clipboard and browsers for a URL."""
    ctx = Context(wf)
    ICON_CLIPBOARD = ctx.icon('clipboard')

    items = []
    url = clipboard_url()
    if url:
        items.append(dict(title='Clipboard', subtitle=url, autocomplete=url,
                          icon=ICON_CLIPBOARD))

    # Browsers
    cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', JXA_RUNNING] + \
        BROWSERS.keys()
    output = subprocess.check_output(cmd)
    running = json.loads(output)

    for name in BROWSERS:
        app, script = BROWSERS[name]
        if not running[name]:
            log.debug('"%s" not running', name)
            continue
        log.debug('fetching current tab from "%s" ...', name)

        script = script % dict(appname=name)
        cmd = ['/usr/bin/osascript', '-l', 'JavaScript', '-e', script]
        output = subprocess.check_output(cmd)
        data = json.loads(output)
        if not data:
            log.debug('no URL for "%s"', name)
            continue
        title = data['title'] or 'Untitled'
        url = data['url']
        items.append(dict(title=title, subtitle=url, autocomplete=url,
                          icon=app, icontype='fileicon'))

    if not items:
        wf.add_item('No Clipboard or Browser URL',
                    'Enter a URL or copy one to clipboard.',
                    icon=ICON_WARNING)

    for item in items:
        wf.add_item(**item)

    wf.send_feedback()


def do_import_search(wf, url):
    """Parse URL for OpenSearch config."""
    from workflow import web
    from searchio import opensearch

    ctx = Context(wf)
    ICON_ERROR = ctx.icon('error')
    ICON_IMPORT = ctx.icon('import')
    error = None

    log.info('importing "%s" ...', url)
    try:
        search = opensearch.parse(url)
    except opensearch.NoAutoSuggest:
        error = 'Autosuggest is not supported'
    except opensearch.Invalid:
        error = "Couldn't parse OpenSearch definition"
    except opensearch.NotFound:
        error = "Site doesn't support OpenSearch"

    if error:
        wf.add_item(error, icon=ICON_ERROR)
        wf.send_feedback()
        return

    icon = wf.workflowfile('icons/icon.png')
    item_icon = ICON_IMPORT
    if search.icon_url:
        log.info('fetching search icon ...')
        p = wf.datafile('icons/{}.png'.format(search.uid))
        try:
            r = web.get(search.icon_url)
            r.raise_for_status()
        except Exception as err:
            log.error('error fetching icon (%s): %r', search.icon_url, err)
        else:
            r.save_to_path(p)
            icon = p
            item_icon = p

    it = wf.add_item(u'Add "{}"'.format(search.name),
                     u'↩ to add search',
                     valid=True,
                     icon=item_icon)

    it.setvar('engine', 'OpenSearch')
    it.setvar('uid', search.uid)
    it.setvar('title', search.name)
    it.setvar('name', search.name)
    it.setvar('icon', icon)
    # it.setvar('jsonpath', search.jsonpath)
    it.setvar('search_url', search.search_url)
    it.setvar('suggest_url', search.suggest_url)

    wf.send_feedback()


def run(wf, argv):
    """Run ``searchio web`` sub-command."""
    args = docopt(usage(wf), argv)
    url = args.get('<url>')
    if not url:
        return do_get_url(wf, args)

    return do_import_search(wf, url)
