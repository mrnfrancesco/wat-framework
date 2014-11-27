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

__all__ = ['clients']

from pycurl import *

from singleton.singleton import Singleton

import wat


@Singleton
class clients(object):
    """
    Collect all the curl client options to use as default on client initialization.
    These options mirrors the one on libcurl, so you can see <http://curl.haxx.se/libcurl/c/curl_easy_setopt.html>
    for a complete list of all the available options, their meaning and default values.

    You could modify options:
        * **here**, to make them available on every framework start
        * **programmatically**, to make them available on that start only
    """

    __all__ = {
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

    # BEHAVIOR OPTIONS
    VERBOSE = False
    NOPROGRESS = True
    NOSIGNAL = False

    # CALLBACK OPTIONS
    # all defaults are good for our purpose, but feel free to override them IN YOUR CURL CLIENT INSTANCE
    # in case you want to show some information in a different manner (e.g. progress information)

    # ERROR OPTIONS
    FAILONERROR = False  # specify if curl have to fail on 4xx response status code

    # NETWORK OPTIONS
    # Accettable values are:
    #   <default>                       no proxy, but environmental one will be used
    #   "" (empty string)               no proxy, environmental one will be ignored
    #   "scheme://(hostname|ip):port"   use the specified proxy
    # PROXY = ""
    PORT = 80  # default port to use to make requests

    # NAMES and PASSWORDS OPTIONS (Authentication)
    # PROXYUSERNAME = "username"
    # PROXYPASSWORD = "password"

    # HTTP OPTIONS
    AUTOREFERER = False
    FOLLOWLOCATION = False  # same of MAXREDIRS = 0
    USERAGENT = "/".join([wat.project.name, wat.project.version])
    HTTPHEADER = []
    HTTP_VERSION = CURL_HTTP_VERSION_NONE  # pycurl will use whatever it thinks fit

    # TFTP OPTIONS
    # FTP OPTIONS
    # PROTOCOL OPTIONS

    # CONNECTION OPTIONS
    TIMEOUT = 0  # no timeout for the entire request
    FRESH_CONNECT = True  # same of HEADER = ["Connection: close",]
    CONNECTTIMEOUT = 30

    # SSL and SECURITY OPTIONS
    # SSH OPTIONS
    # OTHER OPTIONS