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

from datetime import date
from pycurl import *

from it.mrnfrancesco.framework.wat.lib.modules import MetaModule, info
from it.mrnfrancesco.framework.wat.lib.models import Author
from it.mrnfrancesco.framework.wat.lib.properties import Property, Constraint
from it.mrnfrancesco.framework.wat.lib import clients
from it.mrnfrancesco.framework.wat.modules.website import cms


@info(
    authors=[
        Author(email="francesco.mrn24@gmail.com", name="Francesco Marano", nickname="mrnfrancesco"),
    ],
    released=date(2014, 10, 18),
    updated=date(2014, 10, 18),
    version='0.0.1',
    provides=[
        Property("website.cms.opencart.version"),
    ],
    dependencies=[
        Constraint("website.cms.name", cms.Name("opencart"), 'eq'),
        Property("website.cms.opencart.admin.directory"),
    ]
)
class GetVersionByFooter(object):
    """This module provide the OpenCart exact version by looking at the admin page footer unless it is disabled."""
    __metaclass__ = MetaModule

    @staticmethod
    def check():
        return True

    @staticmethod
    def run():
        curl = clients.Curl()
        _ = curl.setopt
        _(URL, "localhost")
        _(PORT, 1234)
        # curl.perform()