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

from datetime import date
from pycurl import URL, WRITEFUNCTION, HTTP_CODE
from wat import conf
from wat.lib import clients

from wat.lib.components import WatComponent, info, MetaComponent
from wat.lib.exceptions import ComponentFailure
from wat.lib.models import Author
from wat.lib.properties import Constraint


@info(
    authors=[
        Author(email="francesco.mrn24@gmail.com", name="Francesco Marano", nickname="mrnfrancesco"),
    ],
    released=date(2014, 11, 15),
    updated=date(2014, 11, 15),
    version='0.0.1',
    preconditions=[
        Constraint("website.cms.name", "opencart", 'eq'),
    ]
)
class GetAdminDirByDefault(WatComponent):
    """This module provide the OpenCart default admin directory or fail if it was changed."""
    __metaclass__ = MetaComponent

    def __init__(self):
        super(GetAdminDirByDefault, self).__init__()
        from urlparse import urljoin

        self.curl = clients.Curl()
        self.curl.setopt(URL, urljoin(conf.clients.instance().URL, 'admin/'))

    def run(self):
        self.curl.perform()
        http_code = self.curl.getinfo(HTTP_CODE)
        if http_code is 200:
            return 'admin/'
        elif http_code is 404:
            raise ComponentFailure('Admin directory name is not the default one')
        else:
            raise ComponentFailure("Server response HTTP status code was '%d', 200 or 404 expected" % http_code)
