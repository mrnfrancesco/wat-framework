import re
from datetime import date
from pycurl import URL, HTTP_CODE, HTTPPOST, EFFECTIVE_URL, FOLLOWLOCATION, WRITEFUNCTION, HEADERFUNCTION

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
    updated=date(2015, 01, 02),
    version='0.1.0',
    preconditions=[
        Constraint("website.cms.name", "opencart", 'eq'),
        Property("website.cms.opencart.admin.directory"),
        Property("website.cms.opencart.admin.credentials"),
    ]
)
class GetAdminSessionByLogin(WatComponent):
    """Get the OpenCart admin session id and session token to make authenticated requests."""
    __metaclass__ = MetaComponent

    def __init__(self):
        super(GetAdminSessionByLogin, self).__init__()
        from urlparse import urljoin

        def __get_phpsessionid(header):
            print header
            match = re.match("^Set-Cookie: .*PHPSESSID=(?P<phpsessid>[a-z0-9]+);.*$", header)
            if match:
                self.phpsessid = match.group('phpsessid')

        self.phpsessid = None
        self.curl = clients.Curl()
        self.curl.setopt(HEADERFUNCTION, __get_phpsessionid)
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
            if match is not None and self.phpsessid is not None:
                return {
                    'phpsessid': self.phpsessid,
                    'token': match.group('token'),
                }
            elif match is None:
                raise ComponentFailure("Unable to retrieve session token")
            else:
                raise ComponentFailure("Unable to retrieve PHPSESSID cookie")
        else:
            raise ComponentFailure("Server response HTTP status code was %d, 200 expected" % http_code)
