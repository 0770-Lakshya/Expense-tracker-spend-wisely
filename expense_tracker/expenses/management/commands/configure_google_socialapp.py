import os
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Configure Site domain and Google SocialApp from env vars'

    def handle(self, *args, **options):
        self._configure_site()
        self._configure_google_socialapp()

    def _configure_site(self):
        try:
            from django.contrib.sites.models import Site
        except ImportError:
            return

        try:
            domain = os.environ.get('RENDER_EXTERNAL_URL', '').rstrip('/')
            if not domain:
                return
            domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
            Site.objects.update_or_create(
                id=settings.SITE_ID,
                defaults={'domain': domain, 'name': 'Expense Tracker'},
            )
            self.stdout.write(f'Site domain set to {domain}')
        except Exception as e:
            self.stdout.write(f'Skipping site config: {e}')

    def _configure_google_socialapp(self):
        try:
            from allauth.socialaccount.models import SocialApp
        except ImportError:
            self.stdout.write('Skipping SocialApp: allauth not installed')
            return

        try:
            qs = SocialApp.objects.filter(provider='google')
            count = qs.count()
            if count:
                qs.delete()
                self.stdout.write(f'Deleted {count} Google SocialApp record(s)')
            self.stdout.write(self.style.SUCCESS(
                'Google SocialApp will use SOCIALACCOUNT_PROVIDERS settings (env vars)'
            ))
        except Exception as e:
            self.stdout.write(f'Skipping SocialApp config: {e}')
