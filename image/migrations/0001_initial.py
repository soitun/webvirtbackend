# Generated by Django 4.2.3 on 2023-10-27 21:21

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("region", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Image",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(blank=True, max_length=100, null=True, unique=True)),
                (
                    "arch",
                    models.CharField(
                        choices=[("x86_64", "X64"), ("aarch64", "ARM64")], default="x86_64", max_length=50
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("custom", "Custom"),
                            ("backup", "Backup"),
                            ("snapshot", "Snapshot"),
                            ("application", "Application"),
                            ("distribution", "Distribution"),
                        ],
                        default="snapshot",
                        max_length=50,
                    ),
                ),
                (
                    "event",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("create", "Creating"),
                            ("delete", "Deleting"),
                            ("restore", "Restoring"),
                            ("convert", "Converting"),
                            ("transfer", "Transfering"),
                        ],
                        max_length=40,
                        null=True,
                    ),
                ),
                ("md5sum", models.CharField(max_length=50)),
                (
                    "distribution",
                    models.CharField(
                        choices=[
                            ("unknown", "Unknown"),
                            ("debian", "Debian"),
                            ("ubuntu", "Ubuntu"),
                            ("fedora", "Fedora"),
                            ("centos", "CentOS"),
                            ("almalinux", "AlmaLinux"),
                            ("rockylinux", "Rocky Linux"),
                        ],
                        default="unknown",
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True, null=True)),
                ("file_name", models.CharField(max_length=100)),
                ("file_size", models.BigIntegerField(blank=True, null=True)),
                ("disk_size", models.BigIntegerField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=False, verbose_name="Active")),
                ("is_deleted", models.BooleanField(default=False, verbose_name="Deleted")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now_add=True)),
                ("deleted", models.DateTimeField(blank=True, null=True)),
                ("regions", models.ManyToManyField(blank=True, to="region.region")),
            ],
            options={
                "verbose_name": "Image",
                "verbose_name_plural": "Images",
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="ImageError",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event", models.CharField(blank=True, max_length=40, null=True)),
                ("message", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("image", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="image.image")),
            ],
            options={
                "verbose_name": "Image Error",
                "verbose_name_plural": "Image Errors",
                "ordering": ["-id"],
            },
        ),
    ]
