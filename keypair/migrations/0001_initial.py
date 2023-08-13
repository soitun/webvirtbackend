# Generated by Django 4.2.3 on 2023-08-13 17:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("virtance", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="KeyPair",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("name", models.CharField(max_length=255)),
                ("public_key", models.CharField(max_length=1000)),
                ("fingerprint", models.CharField(max_length=50)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "SSH Key",
                "verbose_name_plural": "SSH Keys",
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="KeyPairVirtance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "keypair",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="keypair.keypair",
                    ),
                ),
                (
                    "virtance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="virtance.virtance",
                    ),
                ),
            ],
            options={
                "verbose_name": "SSH Key Virtance",
                "verbose_name_plural": "SSH Keys Virtance",
                "ordering": ["-id"],
            },
        ),
    ]
