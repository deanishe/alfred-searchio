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

from __future__ import print_function, absolute_import


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

HELP_MAIN = u"""\
searchio [<command>] [options] [<query>]

Provide auto-suggestion results for <query>.

<engine> is the ID (short name). View them all with:
    searchio list

Use `list` and `variants` to view the available engines/variants.


Usage:
    searchio search [-e <engine>] [-v <variant>] <query>
    searchio clean
    searchio settings [<query>]
    searchio list [<query>]
    searchio variants [-e <engine>] [<query>]
    searchio -h

Options:
    -e, --engine=<ID>       ID (short name) of search engine to use
                            [default: {engine}]
    -v, --variant=<ID>      ID (short name) of variant to use
                            [default: {variant}]
    -t, --text              Print results as text, not Alfred XML
    -h, --help              Display this help message
"""


HELP_LIST = u"""
Searchio! supported engines
===========================

Use `ID` to specify the engine to `searchio search`, e.g. to search
DuckDuckGo for "socks".

    searchio search -e ddg socks

Use `searchio variants -e <engine>` to see an engine's variants.
"""

HELP_VARIANTS = u"""
Variants for {name}
============={underline}

Use `-v <ID>` to specify a variant, e.g. to search Amazon Germany:

    searchio search -e amazon -v de socken
"""
