import re
from datetime import date
from pycurl import URL, HTTP_CODE, HTTPPOST, EFFECTIVE_URL, FOLLOWLOCATION, WRITEFUNCTION

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
        Property("website.cms.opencart.admin.directory"),
        Property("website.cms.opencart.admin.credentials"),
    ]
)
class GetAdminTokenFromUrl(WatComponent):
    """Get the OpenCart admin token to make authenticated requests."""
    __metaclass__ = MetaComponent

    def __init__(self):
        super(GetAdminTokenFromUrl, self).__init__()
        from urlparse import urljoin

        self.curl = clients.Curl()
        self.curl.setopt(WRITEFUNCTION, self.save_as_attribute('_'))
        self.curl.setopt(FOLLOWLOCATION, True)
        url = urljoin(
            conf.clients.instance().URL,
            self.precondition("website.cms.opencart.admin.directory") + 'index.php?route=common/login'
        )
        self.curl.setopt(URL, url)
        credentials = self.precondition("website.cms.opencart.admin.credentials")
        self.curl.setopt(HTTPPOST, [
            ('username', credentials['username']),
            ('password', credentials['password'])
        ])

    def run(self):
        self.curl.perform()
        http_code = self.curl.getinfo(HTTP_CODE)
        if http_code == 200:
            match = re.match(
                r'.+/index\.php\?route=common/home&token=(?P<token>[0-9a-f]{32})$',
                self.curl.getinfo(EFFECTIVE_URL)
            )
            if match is not None:
                return match.group('token')
            else:
                raise ComponentFailure("Unable to retrieve token from URL")
        else:
            raise ComponentFailure("Server response HTTP status code was %d, 200 expected" % http_code)
