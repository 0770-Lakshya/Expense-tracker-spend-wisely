import os
from django.db import migrations


def deduplicate_google_social_app(apps, schema_editor):
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    Site = apps.get_model('sites', 'Site')

    apps_qs = SocialApp.objects.filter(provider='google').order_by('pk')

    if apps_qs.count() == 0:
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
        secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()
        if client_id and secret:
            app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id=client_id,
                secret=secret,
            )
            site = Site.objects.get_current()
            app.sites.add(site)
        return

    keep = apps_qs.last()
    apps_qs.exclude(pk=keep.pk).delete()

    client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
    secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()
    if client_id:
        keep.client_id = client_id
    if secret:
        keep.secret = secret
    keep.save()

    site = Site.objects.get_current()
    keep.sites.add(site)


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('expenses', '0003_create_google_social_app'),
    ]

    operations = [
        migrations.RunPython(deduplicate_google_social_app, reverse_func),
    ]
