# Generated by Django 3.2.7 on 2021-09-07 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_remove_file_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(upload_to='media'),
        ),
    ]