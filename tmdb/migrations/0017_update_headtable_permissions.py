from django.db import migrations

from tmdb.views.settings_view import update_headtable_group_permissions

def update_permissions(apps, schema_editor):
    update_headtable_group_permissions()

class Migration(migrations.Migration):
    dependencies = [
        ('tmdb', '0016_set_on_delete_behaviour'),
    ]

    operations = [
        migrations.RunPython(update_permissions, update_permissions),
    ]
