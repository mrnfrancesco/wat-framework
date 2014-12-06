from datetime import date
from pycurl import URL, NOBODY, HTTP_CODE

from wat import conf
from wat.lib import clients
from wat.lib.components import *
from wat.lib.exceptions import ComponentFailure
from wat.lib.models import Author


@info(
    authors=[
        Author(email="francesco.mrn24@gmail.com", name="Francesco Marano", nickname="mrnfrancesco"),
    ],
    released=date(2014, 12, 01),
    updated=date(2014, 12, 06),
    version='0.0.2',
    preconditions=None
)
class CheckCmsNameAsOpencart(WatComponent):
    """Check if the target CMS name is OpenCart"""
    __metaclass__ = MetaComponent

    def __init__(self):
        super(CheckCmsNameAsOpencart, self).__init__()
        from urlparse import urljoin

        self.curl = clients.Curl()
        self.curl.setopt(NOBODY, True)
        self.curl.setopt(URL, urljoin(conf.clients.instance().URL, 'catalog/controller/product/product.php'))

    def run(self):
        self.curl.perform()
        http_code = self.curl.getinfo(HTTP_CODE)
        if http_code == 200 or http_code == 500:
            return 'opencart'
        elif http_code == 404:
            raise ComponentFailure('Target CMS seems not to be OpenCart')
        else:
            raise ComponentFailure("Server response HTTP status code was %d, 200 or 404 expected" % http_code)