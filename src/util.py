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
"""

from __future__ import print_function, absolute_import


class Table(object):
    """Pretty-printed text table for the command line.

    Attributes:
        rows (list): The rows of the table.
    """
    def __init__(self, titles=None):
        self.rows = []
        self._str_rows = []
        self._width = None
        if titles:
            self.add_row(titles, True)

    def add_row(self, row, title=False):
        """Add a new row to table.

        Args:
            row (iterable): Items for the row.
        """

        if self.width and len(row) != self.width:
            raise ValueError('Rows must have {} elements, not {}'.format(
                             self.width, len(row)))
        l = []
        for obj in row:
            if isinstance(obj, unicode):
                s = obj.encode('utf-8')
            elif isinstance(obj, str):
                s = obj
            else:
                s = str(obj)

            l.append(s)

        row = [title] + list(l)
        self.rows.append(row)

    @property
    def colwidths(self):
        """Return widths of columns.

        Returns:
            list: `int` width of each column.
        """

    @property
    def width(self):
        """Required length of each row.

        Returns:
            int: Length of first row.
        """

        if self._width is None:

            if not self.rows:
                return None

            self._width = len(self.rows[0]) - 1
            self._colwidths = [0 for _ in range(self._width)]

        return self._width

    def row_to_str(self, row):
        """Convert each object in `row` to a `str`.

        Args:
            row (list): Various objects.

        Returns:
            str: UTF-8 encoded string.
        """

        is_title, data = row[0], row[1:]
        str_row = [is_title]

        for i, cell in enumerate(data):
            if isinstance(cell, unicode):
                cell = cell.encode('utf-8')
            elif isinstance(cell, str):
                pass
            else:
                cell = repr(cell)

            str_row.append(cell)

        return str_row

    def __str__(self):
        """Return UTF-8 representation of data.

        Returns:
            str: UTF-8 string of tabular data.
        """

        widths = [0 for _ in range(self.width)]
        table = []
        for row in self.rows:
            row = self.row_to_str(row)
            for i, s in enumerate(row[1:]):
                j = len(s)
                if j > widths[i]:
                    widths[i] = j

            table.append(row)

        padded = []
        for row in table:
            is_title, cells = row[0], row[1:]
            newrow = [is_title]
            for i, s in enumerate(cells):
                f = '{{:{}s}}'.format(widths[i])
                newrow.append(f.format(s))
            padded.append(newrow)

        hr = [' '] + [('-' * (w+2)) for w in widths] + ['']
        hr = '+'.join(hr)
        text = [hr]
        for row in padded:
            is_title, cells = row[0], row[1:]
            text.append(''.join([' | ',
                                  ' | '.join(cells),
                                  ' | ']))
            if is_title:
                text.append(hr)

        text.append(hr)

        return b'\n'.join(text)
