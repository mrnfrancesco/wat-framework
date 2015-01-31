from datetime import date

from wat.lib.components import WatComponent, info, MetaComponent
from wat.lib.models import Author
from wat.lib.properties import Property

from ..ftp import __parameters__ as parameters


@info(
    authors=[
        Author(email="francesco.mrn24@gmail.com", name="Francesco Marano", nickname="mrnfrancesco"),
    ],
    released=date(2015, 01, 10),
    updated=date(2015, 01, 10),
    version='1.1.0',
    preconditions=[
        Property("website.cms.opencart.settings"),
    ]
)
class GetFtpSettings(WatComponent):
    """Get the OpenCart FTP settings."""
    __metaclass__ = MetaComponent

    def run(self):
        settings = self.precondition('website.cms.opencart.settings')
        return {key.replace('config_ftp_', ''): settings[key] for key in settings if key in parameters}
