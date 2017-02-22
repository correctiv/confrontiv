import json

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.contrib.postgres.fields import JSONField

from .delivery import send_by_email


@python_2_unicode_compatible
class RecipientGroup(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        verbose_name = _('Recipient Group')
        verbose_name_plural = _('Recipient Groups')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Recipient(models.Model):
    name = models.CharField(max_length=512)

    slug = models.SlugField(max_length=255)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)

    groups = models.ManyToManyField(RecipientGroup)

    class Meta:
        verbose_name = _('Recipient')
        verbose_name_plural = _('Recipients')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class InquiryTemplate(models.Model):
    name = models.CharField(max_length=255)

    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True, help_text=_('Is sent to the recipient'))
    intro = models.TextField(blank=True,
                             help_text=_('Appears on the inquiry page'))

    form = JSONField(default=dict)

    class Meta:
        verbose_name = _('Inquiry Template')
        verbose_name_plural = _('Inquiry Templates')

    def __str__(self):
        return self.name

    def get_subject(self, context):
        return self.render(self.subject, context)

    def get_body(self, context):
        return self.render(self.body, context)

    def get_intro(self, context):
        return self.render(self.intro, context)

    def render(self, template_str, context):
        return Template(template_str).render(context)


@python_2_unicode_compatible
class Inquiry(models.Model):
    name = models.CharField(max_length=255)

    created = models.DateTimeField(default=timezone.now)

    template = models.ForeignKey(InquiryTemplate, null=True)
    group = models.ForeignKey(RecipientGroup, null=True)

    class Meta:
        verbose_name = _('Inquiry')
        verbose_name_plural = _('Inquiries')

    def __str__(self):
        return self.name


class InquiryRequestManager(models.Manager):
    def make_context(self, ir, template, data):
        context = dict(template.form)
        context.update({
            'url': settings.SITE_URL + ir.get_absolute_url(),
        })
        context.update(data)
        return context

    def create_from_inquiry(self, inquiry, recipient, data):
        exists = InquiryRequest.objects.filter(inquiry=inquiry,
                                               recipient=recipient).exists()
        if exists:
            return

        slug = self.get_random_unique_slug()
        ir = InquiryRequest(
            slug=slug,
            inquiry=inquiry,
            recipient=recipient,
        )
        template = inquiry.template
        context = self.make_context(ir, template, data)
        template_context = Context(context)
        ir.subject = template.get_subject(template_context)
        ir.body = template.get_body(template_context)
        ir.intro = template.get_intro(template_context)
        ir.context = context
        ir.save()
        return ir

    def get_random_unique_slug(self):
        CHARSET = 'abcdefhikmnpqrstuvwxyz234568'
        LENGTH = 6
        exists = True
        while exists:
            slug = get_random_string(length=LENGTH, allowed_chars=CHARSET)
            exists = InquiryRequest.objects.filter(slug=slug).exists()
        return slug


@python_2_unicode_compatible
class InquiryRequest(models.Model):
    slug = models.SlugField(unique=True)

    inquiry = models.ForeignKey(Inquiry)
    recipient = models.ForeignKey(Recipient)

    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True, help_text=_('Is sent to the recipient'))
    intro = models.TextField(blank=True,
                             help_text=_('Appears on the inquiry page'))
    context = JSONField(default=dict)

    sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(null=True, blank=True)
    sent_by = models.CharField(max_length=20, choices=(
        ('email', _('by email')),
        ('fax', _('by fax')),
    ), blank=True)

    has_response = models.BooleanField(default=False)

    objects = InquiryRequestManager()

    class Meta:
        verbose_name = _('Inquiry Request')
        verbose_name_plural = _('Inquiry Requests')

    def __str__(self):
        return '{} -> {}'.format(self.inquiry, self.recipient)

    def get_absolute_url(self):
        return reverse('confrontiv:confrontiv-inquiry',
                kwargs={'slug': self.slug}, current_app='confrontiv')

    def send_by_email(self):
        result = send_by_email(self)
        if result:
            self.sent = True
            self.sent_date = timezone.now()
            self.sent_by = 'email'
            self.save()
        return result


@python_2_unicode_compatible
class InquiryResponse(models.Model):
    request = models.ForeignKey(InquiryRequest)
    recipient = models.ForeignKey(Recipient)

    response = JSONField(default=dict)

    response_date = models.DateTimeField(default=timezone.now, null=True,
                                         blank=True)

    class Meta:
        verbose_name = _('Inquiry Response')
        verbose_name_plural = _('Inquiry Responses')

    def __str__(self):
        return '{} -> {}'.format(self.recipient, self.request)

    def response_as_json(self):
        return json.dumps(self.response)

    def response_date_as_isoformat(self):
        if self.response_date is not None:
            return self.response_date.isoformat()
