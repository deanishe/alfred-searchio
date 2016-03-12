#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-01
#

"""
"""

from __future__ import print_function, unicode_literals, absolute_import

import logging

import engines

logging.basicConfig(level=logging.DEBUG)

for e in engines.get_engines():
    print(e)

print(e.suggest('poop', 'en'))
