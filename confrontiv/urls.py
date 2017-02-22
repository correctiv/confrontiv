from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from .views import InquiryRequestView, InquiryRequestThanksView

urlpatterns = [
    url(r'^(?P<slug>[^/]+)/$', InquiryRequestView.as_view(),
        name='confrontiv-inquiry'),
    url(r'^(?P<slug>[^/]+)/%s/$' % _('thanks'),
        InquiryRequestThanksView.as_view(),
        name='confrontiv-inquiry_thanks'),
]
