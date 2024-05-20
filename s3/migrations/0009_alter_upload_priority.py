# Generated by Django 3.2.25 on 2024-04-18 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('s3', '0008_alter_upload_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='priority',
            field=models.IntegerField(choices=[(1, 'Lowest Priority'), (2, 'Low Priority'), (3, 'Moderate Priority'), (4, 'High Priority'), (5, 'Highest Priority')], default=1),
        ),
    ]