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