# WAT Framework, make simple to do the complex
# Copyright 2014 Francesco Marano and individual contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = ['Curl', 'CurlMulti', 'CurlShare']

import pycurl

from wat import conf
from wat.lib.exceptions import ImproperlyConfigured


class _CurlClient(object):

    @staticmethod
    def _initializedcurl(cls):
        """
        Instantiate and initialize the specified pyCurl class
        with framework default options.
        :param cls: the pyCurl client class to instantiate
        :type cls: class
        :return: an initialized instance of the specified pyCurl class
        """
        curl = cls()
        client_conf = conf.clients.instance()
        for option in client_conf.__all__:
            if hasattr(client_conf, option) and hasattr(pycurl, option):
                try:
                    curl.setopt(getattr(pycurl, option), getattr(client_conf, option))
                except TypeError as e:
                    raise ImproperlyConfigured(
                        message=e.message + " (option: '%(option)s')",
                        params={'option': option}
                    )
        return curl

    def __new__(cls, pycurl_class, *args, **kwargs):
        return cls._initializedcurl(pycurl_class)


class Curl(_CurlClient):
    """Wrapper for the `pycurl.Curl` class
    :return: a default initialized instance of `pycurl.Curl` class
    :rtype: pycurl.Curl
    """
    def __new__(cls, *args, **kwargs):
        return super(Curl, cls).__new__(cls, pycurl.Curl, args, kwargs)


class CurlMulti(_CurlClient):
    """Wrapper for the `pycurl.CurlMulti` class
    :return: a default initialized instance of `pycurl.CurlMulti` class
    :rtype: pycurl.CurlMulti
    """
    def __new__(cls, *args, **kwargs):
        return super(CurlMulti, cls).__new__(cls, pycurl.CurlMulti)


class CurlShare(_CurlClient):
    """Wwrapper for the `pycurl.CurlShare` class
    :return: a default initialized instance of `pycurl.CurlShare` class
    :rtype: pycurl.CurlShare
    """
    def __new__(cls, *args, **kwargs):
        return super(CurlShare, cls).__new__(cls, pycurl.CurlShare)
