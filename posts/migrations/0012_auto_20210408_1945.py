# Generated by Django 2.2.6 on 2021-04-08 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(max_length=100, verbose_name='Комментарий'),
        ),
    ]
