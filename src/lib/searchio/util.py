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
util.py
=======

General helper functions.
"""

from __future__ import print_function, absolute_import

import logging
import os
import urllib
import subprocess
import sys

log = logging.getLogger('workflow.{0}'.format(__name__))


class CommandError(Exception):
    """Improved exception for exec'd commands.

    Raised by `check_output()` if a command exits with non-zero status.

    Attributes:
        command (list): Command that was run.
        returncode (int): Exit status of command.
        stderr (str): Command's STDERR output.
    """

    def __init__(self, command, returncode, stderr):
        """Create new `CommandError`.

        Args:
            command (sequence): The first argument passed to
                :class:`subprocess.Popen`.
            returncode (int): The exit code of the process.
            stderr (str): The output on ``STDERR`` of the process.
        """
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        super(CommandError, self).__init__(command, returncode, stderr)

    def __str__(self):
        """Prettified error message.

        Returns:
            str: Error message.
        """
        return 'CommandError: {!r} exited with {!r}:\n{}'.format(
            self.command, self.returncode, self.stderr)

    def __unicode__(self):
        """Prettified error message.

        Returns:
            unicode: Error message.
        """
        return u'CommandError: {!r} exited with {!r}:\n{}'.format(
            self.command, self.returncode, self.stderr)

    def __repr__(self):
        """Code-like representation of the error.

        Returns:
            str: String representation of error.
        """
        return str(self)


def check_output(cmd):
    """Run `cmd` with `subprocess` and capture output.

    Args:
        cmd (list): Command to execute (first argument to
            `subprocess.Popen()`).

    Raises:
        CommandError: Raised if command exists with non-zero status.

    Returns:
        str: Output of command (STDOUT).
    """
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    stdout, stderr = proc.communicate()
    if proc.returncode:
        raise CommandError(cmd, proc.returncode, stderr)

    return stdout


def get_system_language():
    """Return system language.

    Defaults to `'en'` if `AppleLanguages` is not set.

    Returns:
        str: Language name, e.g. 'en', 'de'.
    """
    try:
        output = check_output(['defaults', 'read', '-g', 'AppleLanguages'])
    except CommandError as err:
        log.error('Error reading AppleLanguages, defaulting to English:\n%s',
                  err)
        return 'en'

    output = output.strip('()\n ')
    langs = [s.strip('", ') for s in output.split('\n')]
    if not len(langs):
        raise ValueError('Could not determine system language')
    lang = langs[0]
    if len(lang) > 2:
        lang = lang[:2]
    log.debug('System language : %r', lang)
    return lang


def textmode():
    """Return `True` if STDOUT is a tty.

    Returns:
        bool: Whether STDOUT is a tty.
    """
    return sys.stdout.isatty()


def url_encode_dict(dic):
    """Copy of `dic` with values URL-encoded.

    Leave keys unaltered, URL-encode values (i.e. UTF-8 strings).

    Args:
        dic (TYPE): Dictionary whose values to URL-encode.

    Returns:
        dict: New dictionary with URL-encoded values.
    """
    encoded = {}

    for k, v in dic.items():
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        elif not isinstance(v, str):
            v = str(v)
        encoded[k] = urllib.quote_plus(v)

    return encoded


def in_same_directory(*paths):
    """Return `True` if `paths` are all in the same directory.

    Args:
        *paths: Paths.

    Returns:
        bool: `True` if `paths` are "siblings".
    """
    paths = [os.path.abspath(p) for p in paths]
    parent = None
    for path in paths:
        if not parent:
            parent = os.path.dirname(path)

        elif os.path.dirname(path) != parent:
            return False

    return True


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

        # hr = [' '] + [('-' * (w+2)) for w in widths] + ['']
        hr = [('-' * w) for w in widths] + ['--']
        hr = '-'.join(hr)
        text = []
        for row in padded:
            is_title, cells = row[0], row[1:]
            # text.append(''.join([' | ',
            #                      ' | '.join(cells),
            #                      ' | ']))
            text.append(' | '.join(cells))
            if is_title:
                text.append(hr)

        # text.append(hr)

        return '\n'.join(text)
