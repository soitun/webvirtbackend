# Generated by Django 4.2.3 on 2023-10-17 17:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("virtance", "0002_alter_virtance_event"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("network", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ipaddress",
            name="is_float",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="ipaddress",
            name="virtance",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="virtance.virtance"
            ),
        ),
    ]
