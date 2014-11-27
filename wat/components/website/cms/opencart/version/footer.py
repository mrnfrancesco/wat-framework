from datetime import date
from pycurl import URL, WRITEFUNCTION, HTTP_CODE
import re

from wat import conf
from wat.lib import clients
from wat.lib.components import *
from wat.lib.exceptions import ComponentFailure
from wat.lib.models import Author
from wat.components.website.cms.opencart.version import *
from wat.lib.properties import Property, Constraint


@info(
    authors=[
        Author(email="francesco.mrn24@gmail.com", name="Francesco Marano", nickname="mrnfrancesco"),
    ],
    released=date(2014, 10, 18),
    updated=date(2014, 11, 21),
    version='0.2.1',
    preconditions=[
        Constraint("website.cms.name", "opencart", 'eq'),
        Property("website.cms.opencart.admin.directory"),
    ]
)
class GetVersionByFooter(WatComponent):
    """This module provide the OpenCart exact version by looking at the admin page footer unless it was disabled."""
    __metaclass__ = MetaComponent

    def __init__(self):
        super(GetVersionByFooter, self).__init__()

        from urlparse import urljoin
        admin_url = urljoin(
            conf.clients.instance().URL,
            self.precondition('website.cms.opencart.admin.directory')
        )

        self.curl = clients.Curl()
        self.curl.setopt(URL, admin_url)
        self.curl.setopt(WRITEFUNCTION, self.save_as_attribute('body'))

    def run(self):
        self.curl.perform()
        http_code = self.curl.getinfo(HTTP_CODE)
        if http_code is 200:
            if not self.body:
                raise ComponentFailure('Server sent an empty response')
            else:
                if re.search(r'<div id="footer">', self.body) is not None:
                    match = re.search(r'(?P<version>1\.5\.(?:\d\.)?\d)', self.body)
                    if match is not None:
                        ver = match.group('version')
                        if ver in __versions__:
                            return ver
                        else:
                            raise ComponentFailure("Unrecognized version '%s'" % ver)
                    else:
                        raise ComponentFailure('Version not found')
                elif re.search(r'<footer id="footer">', self.body) is not None:
                    if __last_version__ == '2.0.0.0':
                        return '2.0.0.0'
                    else:
                        raise ComponentFailure('Cannot determine the exact version (>= 2.0.0.0 found)')
                else:
                    raise ComponentFailure('Cannot determine opencart version')
        else:
            raise ComponentFailure("Server response HTTP status code was '%d', 200 expected" % http_code)
