# WAT Framework, make simple to do the complex
# Copyright (C) 2014  Francesco Marano and individual contributors.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__all__ = ['Curl', 'CurlMulti', 'CurlShare']

import pycurl

from it.mrnfrancesco.framework.wat import conf
from it.mrnfrancesco.framework.wat.lib.exceptions import ImproperlyConfigured


def __initializedcurl(cls):
    curl = cls()
    for option in conf.clients.instance().__slots__:
        if hasattr(conf.clients, option) and hasattr(pycurl, option):
            try:
                curl.setopt(getattr(pycurl, option), getattr(conf.clients.instance(), option))
            except TypeError as e:
                raise ImproperlyConfigured(
                    message=e.message + " (option: %(option)s)",
                    params={'option': option}
                )
    return curl


def Curl():
    """Fake wrapper for the `pycurl.Curl` class
    :return: a default initialized instance of `pycurl.Curl` class
    :rtype: pycurl.Curl
    """
    return __initializedcurl(pycurl.Curl)


def CurlMulti():
    """Fake wrapper for the `pycurl.CurlMulti` class
    :return: a default initialized instance of `pycurl.CurlMulti` class
    :rtype: pycurl.CurlMulti
    """
    return __initializedcurl(pycurl.CurlMulti)


def CurlShare():
    """Fake wrapper for the `pycurl.CurlShare` class
    :return: a default initialized instance of `pycurl.CurlShare` class
    :rtype: pycurl.CurlShare
    """
    return __initializedcurl(pycurl.CurlShare)
