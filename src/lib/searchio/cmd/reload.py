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
    searchio reload
    searchio -h

Options:
    -h, --help     Display this help message

"""

from __future__ import print_function, absolute_import

from docopt import docopt
from searchio import util

log = util.logger(__name__)


def usage(wf=None):
    """CLI usage instructions."""
    return __doc__


def run(wf, argv):
    """Run ``searchio reload`` sub-command."""
    args = docopt(usage(wf), argv)
    log.debug('args=%r', args)
    # TODO: Implement reload
    raise NotImplementedError('searchio reload is not implemented')
