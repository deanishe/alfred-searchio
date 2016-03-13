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
import os
import sys

logging.basicConfig(level=logging.DEBUG)

libpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))
engine_path = os.path.join(libpath, 'searchio/engines')

if libpath not in sys.path:
    sys.path.insert(0, libpath)


from searchio.engines import Manager

em = Manager()
em.load_engines(engine_path)

for engine in em.engines:
    print(engine)
    v = engine.variants.keys()[0]
    print(engine.suggest('poop', v))
