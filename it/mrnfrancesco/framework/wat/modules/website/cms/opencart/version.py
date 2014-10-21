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

__all__ = ['GetVersionByFooter']

__versions__ = ['1.5.4', '1.5.4.1', '1.5.5.1', '1.5.6', '1.5.6.1', '1.5.6.2', '1.5.6.3', '1.5.6.4', '2.0.0.0']
__last_version__ = __versions__[-1]

from datetime import date
from pycurl import *
import re

from it.mrnfrancesco.framework.wat.lib.modules import *
from it.mrnfrancesco.framework.wat.lib.models import Author
from it.mrnfrancesco.framework.wat.lib.properties import Property, Constraint


@info(
    authors=[
        Author(email="francesco.mrn24@gmail.com", name="Francesco Marano", nickname="mrnfrancesco"),
    ],
    released=date(2014, 10, 18),
    updated=date(2014, 10, 21),
    version='0.0.1',
    provides=['version'],
    dependencies=[
        Constraint("website.cms.name", "opencart", 'eq'),
        Property("website.cms.opencart.admin.directory"),
    ]
)
class GetVersionByFooter(WatModule):
    """This module provide the OpenCart exact version by looking at the admin page footer unless it was disabled."""
    __metaclass__ = MetaModule

    __NEW_FOOTER_REGEX = r'<footer id="footer">'
    __OLD_FOOTER_REGEX = r'<div id="footer">' \
                         r'<a href="http://www\.opencart\.com">OpenCart</a>' \
                         r' &copy; 2009-2014 All Rights Reserved\.' \
                         r'<br />Version (?P<version>1\.5\.(?:\d\.)?\d)</div>'

    def __init__(self):
        super(GetVersionByFooter, self).__init__()
        _ = self.curl.setopt
        _(URL, "localhost")
        _(PORT, 1234)
        self.body = None

        def body(string):
            self.body = string

        _(WRITEFUNCTION, body)
        self.ver = None

    def __pick_version(self):
        match = re.search(self.__OLD_FOOTER_REGEX, self.body)
        if match is not None:
            ver = match.group('version')
            if ver in __versions__:
                self.ver = ver
        elif re.search(self.__NEW_FOOTER_REGEX, self.body):
            self.ver = '2.0.0.0'
        return self.ver

    def check(self):
        self.curl.perform()
        if self.curl.getinfo(HTTP_CODE) is 200:
            if not self.body:
                return False
            elif self.__pick_version() is None:
                return False
            else:
                return True

    def run(self):
        if self.ver is not None:  # already got it
            # TODO: set it in some way in the global registry
            return {'version': self.ver}
        else:
            self.curl.perform()
            if self.curl.getinfo(HTTP_CODE) is 200:
                if not self.body:
                    raise  # TODO: found a proper error to raise
                elif self.__pick_version() is not None:
                    return {'version': self.ver}
                else:
                    raise  # TODO: raise a sort of ModuleFailure error
            else:
                raise  # TODO: raise the proper error to say something like 'it is not module fault, it's website one'