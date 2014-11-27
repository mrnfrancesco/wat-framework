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
        self.curl.setopt(WRITEFUNCTION, self.save_as_attribute('_'))
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
