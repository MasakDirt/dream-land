# Generated by Django 5.1 on 2024-08-22 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dream", "0003_rename_photo_profile_profile_picture"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="category",
            options={"verbose_name_plural": "Categories"},
        ),
        migrations.AlterModelOptions(
            name="commentary",
            options={"verbose_name_plural": "Commentaries"},
        ),
        migrations.AlterField(
            model_name="emotion",
            name="recurrence_count",
            field=models.IntegerField(db_default=0),
        ),
        migrations.AlterField(
            model_name="symbol",
            name="recurrence_count",
            field=models.IntegerField(db_default=0),
        ),
        migrations.AlterField(
            model_name="user",
            name="date_joined",
            field=models.DateTimeField(),
        ),
    ]
