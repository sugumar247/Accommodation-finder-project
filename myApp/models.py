from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accommodation_id = models.CharField(max_length=100)  # Assuming the accommodation ID is a string
    property_name = models.CharField(max_length=255)
    property_title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    total_area = models.IntegerField()
    description = models.TextField()
    total_rooms = models.IntegerField()
    balcony = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    property_type = models.CharField(max_length=100)
    bhk = models.IntegerField()
    room_type = models.CharField(max_length=100)
    amenities = models.TextField()
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.property_name}"
