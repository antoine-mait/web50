# Generated by Django 5.1.3 on 2025-03-21 15:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("network", "0006_post_count_likes"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="follow",
            name="follow",
        ),
        migrations.AddField(
            model_name="follow",
            name="profile",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="followers",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="follow",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="following",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
