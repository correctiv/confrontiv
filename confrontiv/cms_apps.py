from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class ConfrontivApp(CMSApp):
    name = _('Confrontiv App')
    app_name = 'confrontiv'
    urls = ['confrontiv.urls']


apphook_pool.register(ConfrontivApp)
