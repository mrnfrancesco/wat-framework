from datetime import date
import logging
from pycurl import URL, NOBODY, HTTP_CODE

from wat import conf
from wat.lib import clients
from wat.lib.components import WatComponent, info, MetaComponent
from wat.lib.exceptions import ComponentFailure
from wat.lib.models import Author
from wat.lib.properties import Constraint
from wat.lib.shortcuts import hierlogger as logger


@info(
    authors=[
        Author(email="francesco.mrn24@gmail.com", name="Francesco Marano", nickname="mrnfrancesco"),
    ],
    released=date(2014, 11, 21),
    updated=date(2014, 12, 18),
    version='0.0.3',
    preconditions=[
        Constraint("website.cms.name", "opencart", 'eq'),
    ]
)
class GetAdminDirByBruteforce(WatComponent):
    """Provide the OpenCart admin directory trying some common ones."""
    __metaclass__ = MetaComponent

    def __init__(self):
        super(GetAdminDirByBruteforce, self).__init__()

        self.curl = clients.Curl()
        self.curl.setopt(NOBODY, True)
        self.admin_dirs = ['admin/', 'administrator/', 'administration/', 'sysadmin/']

    def run(self):
        from urlparse import urljoin
        debug_enabled = logger().isEnabledFor(logging.DEBUG)

        for admin_dir in self.admin_dirs:
            self.curl.setopt(URL, urljoin(conf.clients.instance().URL, 'admin/'))
            self.curl.perform()
            http_code = self.curl.getinfo(HTTP_CODE)
            if http_code in (200, 401):
                return admin_dir
            elif debug_enabled:
                if http_code == 404:
                    logger().debug("Admin directory name is not '%s'" % admin_dir)
                else:
                    logger().debug("Server response HTTP status code was %d, 200 or 404 expected" % http_code)

        raise ComponentFailure(message="Cannot determine admin directory name")
