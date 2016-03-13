#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-12
#

"""
Generate Google JSON variants configuration based on `google-languages.tsv`
"""

from __future__ import print_function, unicode_literals, absolute_import

import json
import os


source = os.path.join(os.path.dirname(__file__), 'google-languages.tsv')


def main():
    result = {}
    with open(source) as fp:
        for line in fp:
            line = line.decode('utf-8').strip()
            if not line:
                continue
            id_, name = line.split('\t')
            result[id_] = {'name': name, 'vars': {'hl': id_}}

    print(json.dumps({'variants': result},
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
