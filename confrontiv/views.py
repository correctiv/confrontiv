from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse

from .models import InquiryRequest
from .forms import create_formclass_from_dict


class InquiryRequestView(UpdateView):
    model = InquiryRequest

    def get_form_class(self):
        self.object = self.get_object()
        return create_formclass_from_dict(self.object.context)

    def get_queryset(self):
        return super(InquiryRequestView, self).get_queryset(
                ).select_related('inquiry')

    def get_success_url(self):
        self.object = self.get_object()
        return reverse('confrontiv:confrontiv-inquiry_thanks', kwargs={
            'slug': self.object.slug})


class InquiryRequestThanksView(DetailView):
    model = InquiryRequest
