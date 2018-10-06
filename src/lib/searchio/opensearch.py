#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-10
#

"""Parse an OpenSearch for search and autosuggest URLs."""

from __future__ import print_function, absolute_import

import re
from urlparse import urljoin, urlparse
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup as BS
from workflow import web

from searchio import util

log = util.logger(__name__)

NS = {
    'os': 'http://a9.com/-/spec/opensearch/1.1/',
    'moz': 'http://www.mozilla.org/2006/browser/search/',
}


class OpenSearchError(Exception):
    """Base exception."""


class NotFound(OpenSearchError):
    """No OpenSearch found."""


class Invalid(OpenSearchError):
    """Missing required attributes."""


class NoAutoSuggest(Invalid):
    """Doesn't support autosuggestions."""


class OpenSearch(object):
    """OpenSearch parameters."""

    def __init__(self):
        self.name = None
        self.description = None
        self.suggest_url = None
        self.search_url = None
        self.icon_url = None
        self.uid = None
        self.jsonpath = '$[1][*]'

    def validate(self):
        if not self.name:
            raise Invalid('missing "name" attribute')
        if not self.search_url:
            raise Invalid('missing "search_url" attribute')
        if not self.suggest_url:
            raise NoAutoSuggest()

    def __unicode__(self):
        return (u'OpenSearch({o.name}) search={o.search_url}, '
                'suggest={o.suggest_url}'.format(o=self))

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return str(self)


def _parse_html(s, baseurl):
    """Extract OpenSearch link and icon from HTML."""
    # TODO: find an icon, e.g. apple-touch-icon
    defurl = iconurl = None
    matchsize = re.compile(r'(\d+)x.*').match

    soup = BS(s, 'html.parser')
    link = soup.find('link', type='application/opensearchdescription+xml')
    if not link:
        return None, None

    defurl = urljoin(baseurl, link['href'])
    log.debug('[opensearch] definition URL: %s', defurl)

    # Find icon
    icons = []
    for elem in soup.find_all('link', rel='apple-touch-icon'):
        size = elem.get('sizes') or '0x0'
        m = matchsize(size)
        if m:
            size = int(m.group(1))
        else:
            size = 0

        url = elem['href']
        icons.append((size, url))

    if icons:  # choose largest icon
        icons.sort()
        iconurl = urljoin(baseurl, icons[-1][1])

    return defurl, iconurl


def _parse_definition(s):
    """Parse an OpenSearch definition."""
    search = OpenSearch()
    root = ET.fromstring(s.encode('utf-8'))

    def tag2attrib(tag, attrib):
        elem = root.find(tag, NS)
        if elem is not None:
            setattr(search, attrib, elem.text.strip())

    tag2attrib('os:ShortName', 'name')
    tag2attrib('os:Description', 'description')

    for elem in root.findall('os:Url', NS):
        t = elem.get('type')
        tpl = elem.get('template')
        if not tpl:
            log.warning('[opensearch] Url has no template')
            continue

        if t == 'text/html':
            search.search_url = tpl.replace('{searchTerms}', '{query}')
        if t == 'application/x-suggestions+json':
            search.suggest_url = tpl.replace('{searchTerms}', '{query}')

    log.debug('[opensearch] %s', search)
    return search


def _is_xml(s):
    """Return ``True`` if string is an XML document."""
    return s.lower().strip().startswith('<?xml ')


def _url2uid(url):
    """Generate a UID for a search based on its URL."""
    p = urlparse(url)
    return 'opensearch-' + p.netloc.replace(':', '-')


def parse(url):
    """Parse a URL for OpenSearch specification."""
    log.info('[opensearch] fetching "%s" ...', url)
    defurl = iconurl = None

    # Fetch and parse URL
    r = web.get(url)
    r.raise_for_status()
    s = r.text

    if not _is_xml(s):  # find URL of OpenSearch definition
        defurl, iconurl = _parse_html(s, url)
        if not defurl:
            log.error('[opensearch] no OpenSearch link found')
            raise NotFound(url)

        r = web.get(defurl)
        r.raise_for_status()
        s = r.text

    # Parse OpenSearch definition
    search = _parse_definition(s)
    search.validate()

    search.uid = _url2uid(url)
    search.icon_url = iconurl

    return search
