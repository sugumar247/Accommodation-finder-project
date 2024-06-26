# Generated by Django 5.0.3 on 2024-06-06 08:49

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
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accommodation_id', models.CharField(max_length=100)),
                ('property_name', models.CharField(max_length=255)),
                ('property_title', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('location', models.CharField(max_length=255)),
                ('total_area', models.IntegerField()),
                ('description', models.TextField()),
                ('total_rooms', models.IntegerField()),
                ('balcony', models.CharField(max_length=10)),
                ('city', models.CharField(max_length=100)),
                ('property_type', models.CharField(max_length=100)),
                ('bhk', models.IntegerField()),
                ('room_type', models.CharField(max_length=100)),
                ('amenities', models.TextField()),
                ('booking_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
