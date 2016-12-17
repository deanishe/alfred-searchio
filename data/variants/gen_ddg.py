#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-12-17
#

"""Generate Duck Duck Go variants."""

from __future__ import print_function, absolute_import

import json
import os


source = os.path.join(os.path.dirname(__file__), 'variants-ddg.tsv')


def main():
    result = {}
    with open(source) as fp:
        for line in fp:
            line = line.decode('utf-8').strip()
            if not line:
                continue
            id_, name = line.split('\t')
            result[id_] = {'name': name, 'vars': {'region': id_}}

    print(json.dumps({'variants': result},
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
