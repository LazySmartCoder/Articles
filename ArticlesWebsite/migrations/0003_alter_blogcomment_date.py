# Generated by Django 5.0.1 on 2024-07-17 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ArticlesWebsite", "0002_alter_blogcomment_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blogcomment",
            name="Date",
            field=models.CharField(default="2024-07-17 21:42:29.704670", max_length=40),
        ),
    ]
