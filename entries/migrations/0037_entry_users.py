# Generated by Django 4.2.6 on 2023-10-16 13:01

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0036_sessionentry_kit_inspected'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntryUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4)),
                ('last_login', models.DateField(blank=True, null=True)),
                ('competition_entry', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='entries.competitionentry')),
            ],
        ),
    ]
