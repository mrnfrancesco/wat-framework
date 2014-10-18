from datetime import date
from pycurl import *

from it.mrnfrancesco.framework.wat.lib.modules import AbstractBaseModule
from it.mrnfrancesco.framework.wat.lib.models import Author
from it.mrnfrancesco.framework.wat.lib.properties import Property, Constraint


class GetVersionByFooter(AbstractBaseModule):
    """This module provide the OpenCart exact version by looking at the admin page footer unless it is disabled."""

    @property
    def authors(self):
        return [
            Author(
                email="francesco.mrn24@gmail.com",
                name="Francesco Marano",
                nickname="mrnfrancesco",
                url="http://mrnfrances.co"
            ),
        ]

    @property
    def release_date(self):
        return date(year=2014, month=10, day=12)

    @property
    def last_update(self):
        return date(year=2014, month=10, day=16)

    @property
    def dependencies(self):
        return [
            Constraint("website::cms::name", "opencart"),
            Property("opencart::admin::directory::name"),
        ]

    @property
    def provides(self):
        return [
            Property("opencart::version"),
        ]

    def check(self):
        return True

    def run(self):
        from it.mrnfrancesco.framework.wat.lib import clients
        curl = clients.Curl()
        _ = curl.setopt
        _(URL, "localhost")
        _(PORT, 1234)
        curl.perform()

        print '1.5.5.1'


if __name__ == '__main__':
    GetVersionByFooter().run()
