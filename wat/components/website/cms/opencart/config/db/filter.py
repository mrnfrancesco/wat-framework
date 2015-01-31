from datetime import date

from wat.lib.components import WatComponent, info, MetaComponent
from wat.lib.models import Author
from wat.lib.properties import Property

from ..db import __parameters__ as parameters


@info(
    authors=[
        Author(email="francesco.mrn24@gmail.com", name="Francesco Marano", nickname="mrnfrancesco"),
    ],
    released=date(2015, 01, 10),
    updated=date(2015, 01, 10),
    version='1.1.0',
    preconditions=[
        Property("website.cms.opencart.config"),
    ]
)
class GetDbConfig(WatComponent):
    """Get the OpenCart database configuration parameters."""
    __metaclass__ = MetaComponent

    def run(self):
        config = self.precondition('website.cms.opencart.config')
        return {key.replace('DB_', '').lower(): config[key] for key in config if key in parameters}
