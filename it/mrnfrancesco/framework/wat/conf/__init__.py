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

from os.path import join, dirname
from pycurl import *

from it.mrnfrancesco.framework import wat


class dirs(object):

    __slots__ = {'install', 'lib', 'modules', 'data', 'doc'}

    install = dirname(__file__)
    lib = join(install, 'lib')
    modules = join(install, 'modules')
    data = join(install, 'data')
    doc = join(install, 'doc')

class files(object):

    __slots__ = {'database', 'useragents'}

    database = join(dirs.modules, 'wat.db')
    useragents = join(dirs.data, 'user-agents.lst')


class clients(object):
    # TODO: finish to write the documentation (above class too)
    """
    see <http://curl.haxx.se/libcurl/c/curl_easy_setopt.html> for a complete list of all the options,
    their meaning and default values
    """
    __slots__ = {
        'VERBOSE', 'NOPROGRESS', 'NOSIGNAL',
        'FAILONERROR',
        'PORT',
        'AUTOREFERER', 'FOLLOWLOCATION', 'USERAGENT', 'HTTPHEADER', 'HTTP_VERSION',
        'TIMEOUT', 'FRESH_CONNECT', 'CONNECTTIMEOUT',
    }

    ### BEHAVIOR OPTIONS ###
    VERBOSE = False
    NOPROGRESS = True
    NOSIGNAL = False

    ### CALLBACK OPTIONS ###
    # all defaults are good for our purpose, but feel free to override them IN YOUR CURL CLIENT INSTANCE
    # in case you want to show some information in a different manner (e.g. progress information)

    ### ERROR OPTIONS ###
    FAILONERROR = False  # specify if curl have to fail on 4xx response status code

    ### NETWORK OPTIONS ###
    # Accettable values are:
    #   <default>                       no proxy, but environmental one will be used
    #   "" (empty string"               no proxy, environmental one will be ignored
    #   "scheme://(hostname|ip):port"   use the specified proxy
    # PROXY = ""
    PORT = 80  # default port to use to make requests

    ### NAMES and PASSWORDS OPTIONS (Authentication) ###
    # PROXYUSERNAME = "username"
    # PROXYPASSWORD = "password"

    ### HTTP OPTIONS ###
    AUTOREFERER = False
    FOLLOWLOCATION = False  # same of MAXREDIRS = 0
    USERAGENT = "/".join([wat.project.name, wat.project.version])
    HTTPHEADER = []
    HTTP_VERSION = CURL_HTTP_VERSION_NONE  # pycurl will use whatever it thinks fit

    ### SMTP OPTIONS ###
    ### TFTP OPTIONS ###
    ### FTP OPTIONS ###
    ### RTSP OPTIONS ###
    ### PROTOCOL OPTIONS ###

    ### CONNECTION OPTIONS ###
    TIMEOUT = 0  # no timeout for the entire request
    FRESH_CONNECT = True  # same of HEADER = ["Connection: close",]
    CONNECTTIMEOUT = 30

    ### SSL and SECURITY OPTIONS ###
    ### SSH OPTIONS ###
    ### OTHER OPTIONS ###
    ### TELNET OPTIONS ###
