import os
from django.db import migrations


def create_google_social_app(apps, schema_editor):
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    Site = apps.get_model('sites', 'Site')

    client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
    secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()

    if not client_id or not secret:
        return

    app, created = SocialApp.objects.update_or_create(
        provider='google',
        defaults={
            'name': 'Google',
            'client_id': client_id,
            'secret': secret,
        },
    )

    site = Site.objects.get_current()
    app.sites.add(site)


def remove_google_social_app(apps, schema_editor):
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    SocialApp.objects.filter(provider='google').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('allauth.socialaccount', '0006_alter_socialaccount_extra_data'),
        ('expenses', '0002_set_site_domain'),
    ]

    operations = [
        migrations.RunPython(create_google_social_app, remove_google_social_app),
    ]
