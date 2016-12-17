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
"""

from __future__ import print_function, unicode_literals, absolute_import

import json
import os
import sys

source = os.path.join(os.path.dirname(__file__), 'wikia-sites.tsv')


def log(*args, **kwargs):
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)


class Wiki(object):

    def __init__(self):
        self.wikis = []

    def add(self, domain, name, language):
        self.wikis.append((domain, name, language))

    @property
    def name(self):
        for d, n, l in self.wikis:
            if l is None:
                return n

        return self.wikis[0][1]

    @property
    def id(self):
        for d, n, l in self.wikis:
            if l is None:
                return d

        return self.wikis[0][0]

    def __str__(self):
        output = [self.name]
        wikis = sorted(self.wikis, key=lambda t: t[2])
        for domain, name, language in wikis:
            output.append('  {0}\t{1}\t{2}'.format(language, name, domain))

        return '\n'.join(output).encode('utf-8')

    def as_json(self):
        d = {
            'name': self.name,
            'id': self.id,
            'search_url': 'http://{domain}/wiki/Special:Search?search={query}',
            'suggest_url': 'http://{domain}/api.php?action=opensearch&search={query}&namespace=0|4|112|114|118',
            'variants': {}
        }
        if not self.wikis:
            d['variants']['*'] = {'name': 'Default',
                                  'vars': {'domain': 'wikia.com',
                                           'language': 'en'}}
        else:
            for domain, name, language in self.wikis:
                sub = domain.replace('.wikia.com', '')
                v = {'name': name, 'vars': {'domain': domain,
                                            'language': language}}
                d['variants'][sub] = v

        return json.dumps(d, indent=2, sort_keys=True)


def parse_wikia(domain):
    sub = domain.replace('.wikia.com', '')
    parts = sub.split('.')
    if len(parts) == 1:
        return parts[-1], None

    return reversed(parts)


def main():
    # wikis = defaultdict(set)
    languages = set()
    entries = []
    with open(source) as fp:
        for line in fp:
            line = line.decode('utf-8').strip()
            if not line:
                continue
            domain, name, language = line.split('\t')
            languages.add(language)
            entries.append((domain, name, language))
            # sub, lang = parse_wikia(domain)
            # if sub not in wikis:
            #     wikis[sub] = Wiki()

            # wikis[sub].add(domain, name, language)

    # Find "root" wikias first
    roots = []
    other = []
    for t in entries:
        parts = t[0].split('.')
        if len(parts) == 3 or parts[0] not in languages:  # no language sub-subdomain.
            roots.append(t)
        else:
            other.append(t)

    log('{0:d} roots, {1:d} others'.format(len(roots), len(other)))

    wikis = {}
    for domain, name, language in roots:
        sub = domain.replace('.wikia.com', '')
        w = Wiki()
        w.add(domain, name, language)
        wikis[sub] = w
        log('domain={0!r}, sub={1!r}, name={2!r}, language={3!r}'.format(
            domain, sub, name, language))

    for domain, name, language in other:
        sub = domain.replace('.wikia.com', '')
        sub = sub.split('.', 1)[1]
        log('domain={0!r}, sub={1!r}, name={2!r}, language={3!r}'.format(
            domain, sub, name, language))
        if sub in wikis:
            wikis[sub].add(domain, name, language)
        else:
            w = Wiki()
            w.add(domain, name, language)
            wikis[sub] = w

    # print(json.dumps({'variants': result},
    #                  sort_keys=True, indent=2))

    for sub in sorted(wikis, key=lambda k: wikis[k].name.lower()):
        # print(sub)
        w = wikis[sub]
        print(w.as_json())


if __name__ == '__main__':
    main()
