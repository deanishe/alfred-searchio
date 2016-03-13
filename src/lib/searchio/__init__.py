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
Searchio!
=========

Alfred 2 search suggestion workflow.
"""

from __future__ import print_function, unicode_literals, absolute_import


DEFAULT_ENGINE = 'google'

UPDATE_SETTINGS = {'github_slug': 'deanishe/alfred-searchio'}
HELP_URL = 'https://github.com/deanishe/alfred-searchio/issues'

# Cache search results for 10 minutes
MAX_CACHE_AGE = 600

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
