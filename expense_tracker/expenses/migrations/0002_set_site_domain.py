import os
from django.db import migrations


RENDER_DOMAIN = 'expense-tracker-spend-wisely.onrender.com'


def update_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    domain = os.environ.get('RENDER_EXTERNAL_URL', f'https://{RENDER_DOMAIN}').rstrip('/').replace('https://', '').replace('http://', '')
    Site.objects.update_or_create(
        id=1,
        defaults={'domain': domain, 'name': 'Expense Tracker'},
    )


def reverse_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.update_or_create(
        id=1,
        defaults={'domain': 'example.com', 'name': 'example.com'},
    )


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_site_domain, reverse_site_domain),
    ]
