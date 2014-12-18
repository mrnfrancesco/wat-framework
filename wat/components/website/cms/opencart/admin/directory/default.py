from datetime import date
from pycurl import URL, NOBODY, HTTP_CODE
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
    updated=date(2014, 12, 18),
    version='0.0.3',
    preconditions=[
        Constraint("website.cms.name", "opencart", 'eq'),
    ]
)
class GetAdminDirByDefault(WatComponent):
    """Provide the OpenCart default admin directory or fail if it was changed."""
    __metaclass__ = MetaComponent

    def __init__(self):
        super(GetAdminDirByDefault, self).__init__()
        from urlparse import urljoin

        self.curl = clients.Curl()
        self.curl.setopt(NOBODY, True)
        self.curl.setopt(URL, urljoin(conf.clients.instance().URL, 'admin/'))

    def run(self):
        self.curl.perform()
        http_code = self.curl.getinfo(HTTP_CODE)
        if http_code in (200, 401):
            return 'admin/'
        elif http_code == 404:
            raise ComponentFailure('Admin directory name is not the default one')
        else:
            raise ComponentFailure("Server response HTTP status code was %d, 200 or 404 expected" % http_code)
