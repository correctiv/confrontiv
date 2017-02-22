from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from django.conf import settings

from ...models import Inquiry, InquiryRequest


class Command(BaseCommand):
    help = "Confrontiv send mail"

    def add_arguments(self, parser):
        parser.add_argument('inquiry_id', type=int)

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)

        try:
            inquiry = Inquiry.objects.get(pk=options['inquiry_id'])
        except Inquiry.DoesNotExist:
            raise CommandError('Inquiry "%s" does not exist' % options['inquiry_id'])

        for ir in InquiryRequest.objects.filter(inquiry=inquiry, sent=False):
            result = ir.send_by_email()
            if result:
                self.stdout.write(self.style.SUCCESS(
                    'Successfully sent inquiry to "%s" via %s' % (ir.recipient, ir.recipient.email)))
            else:
                self.stderr.write('Failed to send inquiry to "%s" via' % (ir.recipient, ir.recipient.email))
