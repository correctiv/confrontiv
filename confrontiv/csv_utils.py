from django.http import StreamingHttpResponse


def export_csv_response(queryset, fields, updater=None, name='export.csv'):
    gen = export_csv(queryset, fields, updater)
    response = StreamingHttpResponse(gen, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % name
    return response


class FakeFile(object):
    # unicodecsv doesn't return values
    # so temp store them in here
    def write(self, string):
        self._last_string = string


def export_csv(queryset, fields, updater=None):
    from django.utils import six

    if six.PY3:
        import csv
    else:
        import unicodecsv as csv

    f = FakeFile()
    if updater is not None:
        fields = list(fields) + updater.next()
    writer = csv.DictWriter(f, fields)
    writer.writeheader()
    yield f._last_string
    for obj in queryset:
        d = {}
        for field in fields:
            try:
                value = getattr(obj, field, '')
            except UnicodeEncodeError:
                value = ''
            if value is None:
                d[field] = ""
            else:
                if callable(value):
                    value = value()
                d[field] = six.text_type(value)
        if updater is not None:
            updater.next()
            d.update(updater.send(obj))
        writer.writerow(d)
        yield f._last_string
