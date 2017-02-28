# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-28 22:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('confrontiv', '0003_inquiryrequest_has_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='inquiryrequest',
            name='from_email',
            field=models.EmailField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='inquirytemplate',
            name='from_email',
            field=models.EmailField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='inquiryrequest',
            name='body',
            field=models.TextField(blank=True, help_text='Is sent to the recipient'),
        ),
        migrations.AlterField(
            model_name='inquiryrequest',
            name='intro',
            field=models.TextField(blank=True, help_text='Appears on the inquiry page'),
        ),
        migrations.AlterField(
            model_name='inquirytemplate',
            name='body',
            field=models.TextField(blank=True, help_text='Is sent to the recipient'),
        ),
        migrations.AlterField(
            model_name='inquirytemplate',
            name='intro',
            field=models.TextField(blank=True, help_text='Appears on the inquiry page'),
        ),
    ]
