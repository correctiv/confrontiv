import json

import unicodecsv

from .models import Recipient, InquiryRequest


def make_inquiry_requests_from_file(inquiry, file):
    reader = unicodecsv.DictReader(file)
    for lineno, line in enumerate(reader, 1):
        try:
            recipient = Recipient.objects.get(slug=line['recipient'])
        except Recipient.DoesNotExist:
            raise ValueError('Recipient on line %s not found' % lineno)
        if not recipient.groups.filter(id=inquiry.group_id).exists():
            raise ValueError('Recipient %s not in inquiry group' % recipient)
        data = json.loads(line['data'])
        InquiryRequest.objects.create_from_inquiry(inquiry, recipient, data)
