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

__all__ = ['clients']

from pycurl import *

from it.mrnfrancesco.framework import wat
from singleton.singleton import Singleton


@Singleton
class clients(object):
    # TODO: finish to write the documentation (above class too)
    """
    see <http://curl.haxx.se/libcurl/c/curl_easy_setopt.html> for a complete list of all the options,
    their meaning and default values
    """

    __slots__ = {
        # BEHAVIOR OPTIONS
        'VERBOSE', 'HEADER', 'NOPROGRESS', 'NOSIGNAL',
        # CALLBACK OPTIONS
        'WRITEFUNCTION', 'WRITEDATA', 'READFUNCTION', 'READDATA', 'IOCTLFUNCTION', 'IOCTLDATA', 'SEEKFUNCTION',
        'OPENSOCKETFUNCTION', 'PROGRESSFUNCTION', 'HEADERFUNCTION', 'DEBUGFUNCTION',
        # ERROR OPTIONS
        'STDERR', 'FAILONERROR',
        # NETWORK OPTIONS
        'URL', 'PROTOCOLS', 'REDIR_PROTOCOLS', 'PROXY', 'PROXYPORT', 'PROXYTYPE', 'NOPROXY', 'HTTPPROXYTUNNEL',
        'SOCKS5_GSSAPI_SERVICE', 'SOCKS5_GSSAPI_NEC', 'INTERFACE', 'LOCALPORT', 'LOCALPORTRANGE',
        'DNS_CACHE_TIMEOUT', 'DNS_USE_GLOBAL_CACHE', 'BUFFERSIZE', 'PORT', 'TCP_NODELAY', 'ADDRESS_SCOPE',
        # NAMES and PASSWORDS OPTIONS (Authentication)
        'NETRC', 'NETRC_FILE', 'USERPWD', 'USERNAME', 'PASSWORD', 'PROXYUSERNAME', 'PROXYPASSWORD',
        'HTTPAUTH', 'PROXYAUTH',
        # HTTP OPTIONS
        'AUTOREFERER', 'FOLLOWLOCATION', 'UNRESTRICTED_AUTH', 'MAXREDIRS', 'POSTREDIR', 'PUT', 'POST', 'POSTFIELDS',
        'POSTFIELDSIZE', 'POSTFIELDSIZE_LARGE', 'COPYPOSTFIELDS', 'HTTPPOST', 'REFERER', 'USERAGENT', 'HTTPHEADER',
        'HTTP200ALIASES', 'COOKIE', 'COOKIEFILE', 'COOKIEJAR', 'COOKIELIST', 'HTTPGET', 'HTTP_VERSION',
        'IGNORE_CONTENT_LENGTH', 'HTTP_CONTENT_DECODING', 'HTTP_TRANSFER_DECODING',
        # TFTP OPTIONS
        'TFTP_BLKSIZE',
        # FTP OPTIONS
        'FTPPORT', 'QUOTE', 'POSTQUOTE', 'PREQUOTE', 'FTPLISTONLY', 'FTPAPPEND', 'FTP_USE_EPRT', 'FTP_USE_EPSV',
        'FTP_CREATE_MISSING_DIRS', 'FTP_RESPONSE_TIMEOUT', 'FTP_ALTERNATIVE_TO_USER', 'FTP_SKIP_PASV_IP', 'FTPSSLAUTH',
        'FTP_SSL_CCC', 'FTP_ACCOUNT', 'FTP_FILEMETHOD',
        # PROTOCOL OPTIONS
        'TRANSFERTEXT', 'PROXY_TRANSFER_MODE', 'CRLF', 'RANGE', 'RESUME_FROM', 'RESUME_FROM_LARGE', 'CUSTOMREQUEST',
        'OPT_FILETIME', 'NOBODY', 'INFILESIZE', 'INFILESIZE_LARGE', 'UPLOAD', 'MAXFILESIZE', 'MAXFILESIZE_LARGE',
        'TIMECONDITION', 'TIMEVALUE',
        # CONNECT OPTIONS
        'TIMEOUT', 'TIMEOUT_MS', 'LOW_SPEED_LIMIT', 'LOW_SPEED_TIME', 'MAX_SEND_SPEED_LARGE', 'MAX_RECV_SPEED_LARGE',
        'MAXCONNECTS', 'FRESH_CONNECT', 'FORBID_REUSE', 'CONNECTTIMEOUT', 'CONNECTTIMEOUT_MS', 'IPRESOLVE',
        'CONNECT_ONLY', 'RESOLVE',
        # SSL and SECURITY OPTIONS
        'SSLCERT', 'SSLCERTTYPE', 'SSLKEY', 'SSLKEYTYPE', 'SSLKEYPASSWD', 'SSLENGINE', 'SSLENGINE_DEFAULT',
        'SSLVERSION', 'SSL_VERIFYPEER', 'CAINFO', 'ISSUERCERT', 'CAPATH', 'CRLFILE', 'SSL_VERIFYHOST', 'OPT_CERTINFO',
        'RANDOM_FILE', 'EGDSOCKET', 'SSL_CIPHER_LIST', 'SSL_SESSIONID_CACHE', 'KRB4LEVEL',
        # SSH OPTIONS
        'SSH_AUTH_TYPES', 'SSH_HOST_PUBLIC_KEY_MD5', 'SSH_PUBLIC_KEYFILE', 'SSH_PRIVATE_KEYFILE', 'SSH_KNOWNHOSTS',
        # OTHER OPTIONS
        'SHARE', 'NEW_FILE_PERMS', 'NEW_DIRECTORY_PERMS',
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

    ### TFTP OPTIONS ###
    ### FTP OPTIONS ###
    ### PROTOCOL OPTIONS ###

    ### CONNECTION OPTIONS ###
    TIMEOUT = 0  # no timeout for the entire request
    FRESH_CONNECT = True  # same of HEADER = ["Connection: close",]
    CONNECTTIMEOUT = 30

    ### SSL and SECURITY OPTIONS ###
    ### SSH OPTIONS ###
    ### OTHER OPTIONS ###