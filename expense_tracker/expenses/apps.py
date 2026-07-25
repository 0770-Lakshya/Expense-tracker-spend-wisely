import os
from django.apps import AppConfig
from django.conf import settings


class ExpensesConfig(AppConfig):
    name = 'expenses'

    def ready(self):
        _configure_site()
        _configure_google_social_app()


def _configure_site():
    try:
        from django.contrib.sites.models import Site
        domain = os.environ.get('RENDER_EXTERNAL_URL', '').rstrip('/').replace('https://', '').replace('http://', '')
        if domain:
            Site.objects.update_or_create(id=settings.SITE_ID, defaults={'domain': domain, 'name': 'Expense Tracker'})
    except Exception:
        pass


def _configure_google_social_app():
    try:
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
        secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()
        if client_id and secret:
            app, _ = SocialApp.objects.update_or_create(
                provider='google',
                defaults={'name': 'Google', 'client_id': client_id, 'secret': secret},
            )
            app.sites.add(Site.objects.get_current())
    except Exception:
        pass
