import os
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Ensure exactly one Google SocialApp exists with env var credentials'

    def handle(self, *args, **options):
        try:
            from allauth.socialaccount.models import SocialApp
            from django.contrib.sites.models import Site
        except ImportError:
            self.stdout.write('Skipping: allauth not installed')
            return

        client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
        secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()

        qs = SocialApp.objects.filter(provider='google').order_by('pk')

        if qs.count() > 1:
            keep = qs.last()
            deleted = qs.exclude(pk=keep.pk).delete()[0]
            self.stdout.write(f'Deleted {deleted} duplicate Google SocialApp(s)')
            app = keep
        elif qs.count() == 1:
            app = qs.first()
            self.stdout.write('Found existing Google SocialApp')
        else:
            app = SocialApp(provider='google')
            self.stdout.write('Creating new Google SocialApp')

        if client_id:
            app.client_id = client_id
        if secret:
            app.secret = secret
        app.name = 'Google'
        app.key = ''
        app.save()

        site = Site.objects.get_current()
        app.sites.add(site)

        self.stdout.write(self.style.SUCCESS(
            f'Google SocialApp configured (client_id={client_id[:8]}...)'
        ))
