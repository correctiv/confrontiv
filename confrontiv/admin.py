from django.contrib import admin
from django.conf.urls import url
from django.shortcuts import redirect, Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.contrib import messages
from django.core.exceptions import PermissionDenied

import unicodecsv

from .core import make_inquiry_requests_from_file
from .csv_utils import export_csv_response
from .models import (RecipientGroup, Recipient, InquiryTemplate, Inquiry,
                     InquiryRequest, InquiryResponse)


class RecipientGroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class RecipientAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'email', 'fax',)
    list_filter = ('groups',)
    actions = ['export_csv']

    def get_urls(self):
        urls = super(RecipientAdmin, self).get_urls()
        my_urls = [
            url(r'^upload-recipients/$',
                self.admin_site.admin_view(self.upload_recipients),
                name='confrontiv-upload-recipients'),
        ]
        return my_urls + urls

    def export_csv(self, request, queryset):
        fields = ('id', 'name', 'slug', 'email', 'phone', 'fax', 'address')
        return export_csv_response(queryset, fields)
    export_csv.short_description = _("Export to CSV")

    def upload_recipients(self, request):
        if not request.method == 'POST':
            raise PermissionDenied
        if not self.has_change_permission(request):
            raise PermissionDenied

        reader = unicodecsv.DictReader(request.FILES['file'])
        for lineno, line in enumerate(reader, 1):
            group = line.pop('group', None)
            if 'slug' not in line:
                line['slug'] = slugify(line['name'])
            recipient = Recipient.objects.create(
                **line
            )
            if group is not None:
                rg = RecipientGroup.objects.get(slug=group)
                recipient.groups.add(rg)

        return redirect('admin:confrontiv_recipient_changelist')


class InquiryTemplateAdmin(admin.ModelAdmin):
    pass


class InquiryAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super(InquiryAdmin, self).get_urls()
        my_urls = [
            url(r'^make-inquiry-requests/$',
                self.admin_site.admin_view(self.admin_make_inquiry_requests),
                name='confrontiv-admin_make_inquiry_requests'),
        ]
        return my_urls + urls

    def admin_make_inquiry_requests(self, request):
        if not request.method == 'POST':
            raise PermissionDenied
        if not self.has_change_permission(request):
            raise PermissionDenied

        try:
            inquiry = Inquiry.objects.get(pk=request.POST.get('inquiry_pk'))
        except Inquiry.DoesNotExist:
            raise Http404

        try:
            make_inquiry_requests_from_file(inquiry, request.FILES['file'])
        except ValueError as e:
            messages.add_message(request, messages.ERROR, e.message)
            return redirect('admin:confrontiv_inquiry_changelist')

        return redirect('admin:confrontiv_inquiryrequest_changelist')


class InquiryRequestAdmin(admin.ModelAdmin):
    raw_id_fields = ('recipient',)
    date_hierarchy = 'sent_date'
    list_display = ('recipient', 'inquiry', 'sent', 'sent_date', 'sent_by')
    list_filter = ('inquiry', 'sent', 'has_response', 'sent_by')


class InquiryResponseAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'request', 'response_date')
    date_hierarchy = 'response_date'
    list_filter = ('request__inquiry',)
    raw_id_fields = ('recipient',)

    actions = ['export_csv']

    def export_csv(self, request, queryset):
        fields = ('request_id', 'recipient_id', 'response_as_json',
                  'response_date_as_isoformat')
        return export_csv_response(queryset, fields)
    export_csv.short_description = _("Export to CSV")


admin.site.register(RecipientGroup, RecipientGroupAdmin)
admin.site.register(Recipient, RecipientAdmin)
admin.site.register(InquiryTemplate, InquiryTemplateAdmin)
admin.site.register(Inquiry, InquiryAdmin)
admin.site.register(InquiryRequest, InquiryRequestAdmin)
admin.site.register(InquiryResponse, InquiryResponseAdmin)
