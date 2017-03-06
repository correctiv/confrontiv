from collections import OrderedDict

from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.bootstrap import StrictButton

from .models import InquiryResponse


FIELD_TYPES = {
    'char': (forms.CharField, {}),
    'text': (forms.CharField, {'widget': forms.Textarea}),
    'boolean': (forms.BooleanField, {}),
    'choice': (forms.ChoiceField, {}),
    'boolchoice': (forms.ChoiceField, {'choices': ((1, _('Yes')),
                                                   (0, _('No'))),
                                       'widget': forms.RadioSelect})
}


def create_field_from_dict(field_dict):
    field_type = field_dict.pop('type')
    klass, special_kwargs = FIELD_TYPES[field_type]
    special_kwargs.update(field_dict)
    return klass(**special_kwargs)


def create_formclass_from_dict(form_dict):
    fields = OrderedDict()

    for field in form_dict['fields']:
        field = dict(field)
        name = field.pop('name')
        fields[name] = create_field_from_dict(field)

    return type('InquiryRequestForm', (InquiryResponseMixin, forms.Form), fields)


class InquiryResponseMixin(object):
    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('instance')

        super(InquiryResponseMixin, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        layout_elements = list(self.fields.keys())

        layout = layout_elements + [
            StrictButton(_(u'Send your response'),
                css_class='btn-success btn-lg', type='submit')
        ]
        self.helper.layout = Layout(*layout)

    def save(self):
        InquiryResponse.objects.create(
            request=self.object,
            recipient=self.object.recipient,
            response=self.cleaned_data
        )
        self.object.has_response = True
        self.object.save()
