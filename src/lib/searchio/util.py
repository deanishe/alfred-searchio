#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-03-12
#

"""General helper functions."""

from __future__ import print_function, absolute_import

import logging
import os
from unicodedata import normalize
import urllib
import re
import subprocess
import sys
from uuid import uuid4


def logger(name):
    return logging.getLogger('workflow.' + name)


log = logger(__name__)


class FileFinder(object):
    """Find named file in sequence of directories.

    Results are cached.

    Attributes:
        dirpaths (sequence): Directories to search in.
        extensions (sequence): File extensions to search for.
    """

    def __init__(self, dirpaths, extensions):
        """Create new FileFinder.

        Args:
            dirpaths (sequence): Directories to search in.
            extensions (sequence): File extensions to search for.

        """
        self.dirpaths = dirpaths
        self.extensions = extensions
        self._hits = {}

    def find(self, name, default=None):
        """Find named file in ``self.dirpaths``.

        ``self.dirpaths`` and ``self.extensions`` are searched
        in order, ``self.dirpaths[0]``/``name``.``self.extensions[0]``
        being the first path tried.

        Args:
            name (str): Name of file (minus extension)
            default (None, optional): Return if file isn't found

        Returns:
            str: Path to file (if found).
        """
        if name in self._hits:
            return self._hits[name]

        for dp in self.dirpaths:
            for x in self.extensions:
                p = os.path.join(dp, '{}.{}'.format(name, x))
                if os.path.exists(p):
                    self._hits[name] = p
                    return p

        return default

    def __iter__(self):
        """Yield all matching in all directories.

        Yields:
            str: Paths to files.
        """
        for dp in self.dirpaths:
            for fn in os.listdir(dp):
                x = os.path.splitext(fn)[1].lstrip('.').lower()
                if x not in self.extensions:
                    continue
                yield os.path.join(dp, fn)


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


def fold_diacritics(s):
    """Fold diacritics.

    Args:
        s (unicode): Unicode string

    Returns:
        unicode: Unicode string containing only ASCII
    """
    s = normalize('NFD', s).encode('ascii', 'ignore')
    return unicode(s)


def slugify(text):
    """Make ID-friendly string.

    Args:
        s (basestring): String to make a slug from.

    Returns:
        unicode: Filepath- and URL-friendly slug containing
            only ASCII
    """
    if isinstance(text, str):
        text = text.decode('utf-8')

    text = fold_diacritics(text).lower()
    text = re.sub(r'[^a-z-]+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-').strip()

    return text


def textmode():
    """Return `True` if STDOUT is a tty.

    Returns:
        bool: Whether STDOUT is a tty.
    """
    return sys.stdout.isatty()


def valid_url(url):
    """Return `True` if URL is valid."""
    return re.match(r'https?://\S+', url) is not None


def uuid():
    """Return a `str` UUID."""
    return str(uuid4())


def _bstr(s):
    """Ensure ``s`` is a `str`.

    UTF-8 encode Unicode, call `str` on everything else.

    """
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    elif not isinstance(s, str):
        s = str(s)
    return s


def mkurl(url, query=None, pcencode=False):
    """Replace ``{query}`` in ``url`` with URL-encoded ``query``.

    Args:
        url (str): URL template
        query (str, optional): Query to insert into ``url``

    Returns:
        str: UTF-8 encoded URL

    """
    if pcencode:
        from urllib import quote
    else:
        from urllib import quote_plus as quote
    if not query:
        return url

    query = _bstr(query)
    url = _bstr(url)
    # Replace ${...} patterns needed by Go
    url = re.sub(r'\$(\{.+?\})', r'\1', url)

    d = dict(query=quote(query))
    for k, v in os.environ.items():
        d[k] = quote(v)

    url = url.format(**d)
    log.debug('pcencode=%r, url=%s', pcencode, url)
    return url


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


def shortpath(path):
    """Return relative or shortened path.

    Args:
        path (str): Path to shorten.

    Returns:
        str: Relative path or path with ~ instead of ``$HOME``.

    """
    cwd = os.path.abspath(os.getcwd()) + '/'
    path = os.path.abspath(path)
    if path.startswith(cwd):
        path = path.replace(cwd, './')
    return path.replace(os.getenv('HOME'), '~')


def getjson(url):
    """Retrieve URL and parse response as JSON.

    Args:
        url (str): URL to fetch

    Returns:
        object: JSON-deserialised HTTP response.

    """
    from workflow import web
    r = web.get(url)
    log.debug('[%s] %s', r.status_code, r.url)
    r.raise_for_status()
    return r.json()


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


def path2uid(p):
    """Return UID based on path.

    UID is lowercase basename without file extension.

    Args:
        p (str): path

    Returns:
        str: UID based on path.

    """
    return os.path.splitext(os.path.basename(p))[0].lower()


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
            if isinstance(obj, str):
                s = obj.decode('utf-8')
            elif isinstance(obj, unicode):
                s = obj
            else:
                s = unicode(obj)

            l.append(s)

        row = [title] + list(l)
        self.rows.append(row)

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
            list: List of Unicode strings.

        """
        is_title, data = row[0], row[1:]
        str_row = [is_title]

        for i, cell in enumerate(data):
            if isinstance(cell, str):
                cell = cell.decode('utf-8')
            elif isinstance(cell, unicode):
                pass
            else:
                cell = unicode(cell)

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
                f = u'{{:{}s}}'.format(widths[i])
                newrow.append(f.format(s))
            padded.append(newrow)

        # hr = [' '] + [('-' * (w+2)) for w in widths] + ['']
        hr = [(u'-' * w) for w in widths]
        hr = u'-+-'.join(hr)
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

        return u'\n'.join(text).encode('utf-8')
