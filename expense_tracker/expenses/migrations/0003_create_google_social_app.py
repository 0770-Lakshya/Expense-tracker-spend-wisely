from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('socialaccount', '0006_alter_socialaccount_extra_data'),
        ('expenses', '0002_set_site_domain'),
    ]

    operations = []
