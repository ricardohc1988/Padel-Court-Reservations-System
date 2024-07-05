from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    zip_code = models.IntegerField()
    phone_number = models.IntegerField()
    image = models.ImageField(upload_to='location_images/', blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.city}, {self.state} - {self.address}'

class Court(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name} - {self.location.name} - {self.location.city}, {self.location.state}'

class Reservation(models.Model):
    HOUR_CHOICES = [(f"{hour:02}:00", f"{hour:02}:00") for hour in range(7, 24)]
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.CharField(max_length=5, choices=HOUR_CHOICES)
    end_time = models.CharField(max_length=5, choices=HOUR_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')

    def __str__(self):
        return f"{self.court.name} - {self.date} - {self.start_time} to {self.end_time}"