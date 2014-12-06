from datetime import date
from pycurl import HEADERFUNCTION, NOBODY
import re

from wat.lib import clients
from wat.lib.components import *
from wat.lib.exceptions import ComponentFailure
from wat.lib.models import Author


@info(
    authors=[
        Author(email="francesco.mrn24@gmail.com", name="Francesco Marano", nickname="mrnfrancesco"),
    ],
    released=date(2014, 12, 06),
    updated=date(2014, 12, 06),
    version='0.0.2',
    preconditions=None
)
class ServerNameByResponseHeader(WatComponent):
    """Retrieve HTTP server name from response header"""
    __metaclass__ = MetaComponent

    def __init__(self):
        super(ServerNameByResponseHeader, self).__init__()

        self.headers = list()
        self.curl = clients.Curl()
        self.curl.setopt(NOBODY, True)
        self.curl.setopt(HEADERFUNCTION, self.headers.append)

    def run(self):
        self.curl.perform()
        pattern = re.compile(r'server:\s(?P<server_name>[a-zA-Z\s]+).*\r\n', re.IGNORECASE)
        for header in self.headers:
            m = pattern.match(header)
            if m is not None:
                server_name = m.group('server_name').strip()
                if server_name:
                    return server_name.lower()
        raise ComponentFailure("No 'server' header provided.")
