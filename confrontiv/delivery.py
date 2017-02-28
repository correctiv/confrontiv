from django.core.mail import send_mail
from django.conf import settings


def send_by_email(ir):
    from_email = ir.from_email
    if not from_email:
        from_email = getattr(settings, 'CONFRONTIV_FROM_EMAIL',
                         settings.DEFAULT_FROM_EMAIL)
    if not ir.recipient.email:
        return False
    success = send_mail(ir.subject, ir.body, from_email, [ir.recipient.email],
                        fail_silently=True)
    return bool(success)
