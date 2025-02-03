# Generated by Django 5.1.2 on 2025-02-03 10:53

import app.mixins
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Post",
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
                ("title", models.CharField(max_length=100)),
                ("content", models.TextField()),
            ],
            options={
                "ordering": ["-id"],
            },
            bases=(app.mixins.ChannelLayerGroupSendMixin, models.Model),
        ),
    ]
