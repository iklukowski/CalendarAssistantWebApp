# Generated by Django 5.1.7 on 2025-03-07 13:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('title', models.CharField(max_length=100)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
