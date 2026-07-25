import os
from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate


class ExpensesConfig(AppConfig):
    name = 'expenses'

    def ready(self):
        post_migrate.connect(_run_setup, sender=self)


def _run_setup(sender, **kwargs):
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
        if not client_id or not secret:
            return

        qs = SocialApp.objects.filter(provider='google').order_by('pk')

        if qs.count() > 1:
            keep = qs.last()
            qs.exclude(pk=keep.pk).delete()
            app = keep
        elif qs.count() == 1:
            app = qs.first()
        else:
            app = SocialApp(provider='google')

        app.name = 'Google'
        app.client_id = client_id
        app.secret = secret
        app.save()

        site = Site.objects.get_current()
        app.sites.add(site)
    except Exception:
        pass
