from pyquery import PyQuery
from datetime import date
from pycurl import URL, HTTP_CODE, WRITEFUNCTION, COOKIE

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
    released=date(2015, 01, 03),
    updated=date(2015, 01, 03),
    version='0.0.1',
    preconditions=[
        Constraint("website.cms.name", "opencart", 'eq'),
        Property("website.cms.opencart.admin.directory"),
        Property("website.cms.opencart.admin.session"),
    ]
)
class GetStoreSettings(WatComponent):
    """ Get the complete OpenCart settings list """
    __metaclass__ = MetaComponent

    def __init__(self):
        super(GetStoreSettings, self).__init__()
        from urlparse import urljoin

        session = self.precondition('website.cms.opencart.admin.session')
        admin_dir = self.precondition("website.cms.opencart.admin.directory")

        self.curl = clients.Curl()
        self.curl.setopt(WRITEFUNCTION, self.save_as_attribute('body'))
        url = urljoin(
            conf.clients.instance().URL,
            admin_dir + 'index.php?route=setting/setting&token=' + session['token']
        )
        self.curl.setopt(URL, url)
        self.curl.setopt(COOKIE, 'PHPSESSID=%s; Path=/' % session['phpsessid'])

    def run(self):
        self.curl.perform()
        http_code = self.curl.getinfo(HTTP_CODE)
        if http_code == 200:
            if not self.body:
                raise ComponentFailure('Server sent an empty response')
            else:
                _ = PyQuery(self.body)
                settings = dict()
                for setting in _('input[type="text"][name^="config_"][value]') +\
                        _('input[type="radio"][name^="config_"][checked="checked"][value]'):
                    settings[setting.name] = setting.value
                for setting in _('textarea[name^="config_"]'):
                    settings[setting.name] = setting.text
                for setting in _('select[name^="config_"] > option[selected="selected"]'):
                    settings[setting.getparent().name] = setting.attrib['value']

                return settings
        else:
            raise ComponentFailure("Server response HTTP status code was %d, 200 expected" % http_code)
