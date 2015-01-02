import re
from datetime import date
from pycurl import URL, HTTP_CODE, HTTPPOST, WRITEFUNCTION, HEADERFUNCTION

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
    version='1.0.0',
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

        def __get_session(header):
            if not self.session.has_key('phpsessid'):
                match = re.match("^Set-Cookie: .*PHPSESSID=(?P<phpsessid>[a-z0-9]{26});.*\r\n", header)
                if match:
                    self.session['phpsessid'] = match.group('phpsessid')
            if not self.session.has_key('token'):
                match = re.match("^Location: .*token=(?P<token>[0-9a-f]{32})\r\n$", header)
                if match:
                    self.session['token'] = match.group('token')

        self.curl = clients.Curl()
        self.session = dict()
        self.curl.setopt(HEADERFUNCTION, __get_session)
        self.curl.setopt(WRITEFUNCTION, self.save_as_attribute('_'))
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
        if http_code == 302:
            if self.session.has_key('phpsessid'):
                if self.session.has_key('token'):
                    return self.session
                else:
                    raise ComponentFailure("Unable to retrieve session token")
            else:
                raise ComponentFailure("Unable to retrieve PHP session ID")
        else:
            raise ComponentFailure("Server response HTTP status code was %d, 200 expected" % http_code)
