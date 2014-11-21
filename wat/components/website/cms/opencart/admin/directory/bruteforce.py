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
import logging
from pycurl import URL, WRITEFUNCTION, HTTP_CODE

from wat import conf
from wat.lib import clients
from wat.lib.components import WatComponent, info, MetaComponent
from wat.lib.exceptions import ComponentFailure
from wat.lib.models import Author
from wat.lib.properties import Constraint
from wat.lib.shortcuts import hierlogger as logger


@info(
    authors=[
        Author(email="francesco.mrn24@gmail.com", name="Francesco Marano", nickname="mrnfrancesco"),
    ],
    released=date(2014, 11, 21),
    updated=date(2014, 11, 21),
    version='0.0.1',
    preconditions=[
        Constraint("website.cms.name", "opencart", 'eq'),
    ]
)
class GetAdminDirByBruteforce(WatComponent):
    """This module try to provide the OpenCart admin directory trying some common ones."""
    __metaclass__ = MetaComponent

    def __init__(self):
        super(GetAdminDirByBruteforce, self).__init__()

        self.curl = clients.Curl()
        self.curl.setopt(WRITEFUNCTION, self.save_as_attribute('_'))
        self.admin_dirs = ['admin/', 'administrator/', 'administration/', 'sysadmin/']

    def run(self):
        from urlparse import urljoin
        debug_enabled = logger().isEnabledFor(logging.DEBUG)

        for admin_dir in self.admin_dirs:
            self.curl.setopt(URL, urljoin(conf.clients.instance().URL, 'admin/'))
            self.curl.perform()
            http_code = self.curl.getinfo(HTTP_CODE)
            if http_code is 200:
                return admin_dir
            elif debug_enabled:
                if http_code is 404:
                    logger().debug("Admin directory name is not '%s'" % admin_dir)
                else:
                    logger().debug("Server response HTTP status code was '%d', 200 or 404 expected" % http_code)