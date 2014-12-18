from datetime import date
from pycurl import URL, NOBODY, HTTP_CODE, HTTPPOST, EFFECTIVE_URL, FOLLOWLOCATION
from wat import conf
from wat.lib import clients

from wat.lib.components import WatComponent, info, MetaComponent
from wat.lib.exceptions import ComponentFailure
from wat.lib.models import Author
from wat.lib.properties import Constraint, Property


@info(
    authors=[
        Author(email="francesco.mrn24@gmail.com", name="Francesco Marano", nickname="mrnfrancesco"),
    ],
    released=date(2014, 12, 18),
    updated=date(2014, 12, 18),
    version='0.0.1',
    preconditions=[
        Constraint("website.cms.name", "opencart", 'eq'),
        Property("website.cms.opencart.admin.directory")
    ]
)
class CheckAdminAdminPair(WatComponent):
    """Check if OpenCart credentials are admin-admin."""
    __metaclass__ = MetaComponent

    def __init__(self):
        super(CheckAdminAdminPair, self).__init__()
        from urlparse import urljoin

        self.curl = clients.Curl()
        self.curl.setopt(NOBODY, True)
        self.curl.setopt(FOLLOWLOCATION, True)
        self.url = urljoin(
            conf.clients.instance().URL,
            self.precondition("website.cms.opencart.admin.directory") + 'index.php?route=common/login'
        )
        self.curl.setopt(URL, self.url)
        self.curl.setopt(HTTPPOST, [
            ('username', 'admin'),
            ('password', 'admin'),
            ('redirect', self.url)
        ])

    def run(self):
        self.curl.perform()
        http_code = self.curl.getinfo(HTTP_CODE)
        if http_code == 200:
            effective_url = self.curl.getinfo(EFFECTIVE_URL)
            if effective_url == self.url:
                raise ComponentFailure("OpenCart credentials are not admin-admin")
            else:
                return {'username': 'admin', 'password': 'admin'}
        else:
            raise ComponentFailure("Server response HTTP status code was %d, 200 expected" % http_code)
