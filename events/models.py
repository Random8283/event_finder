from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, time

# Create your models here.


EVENT_TYPES = [
    ('club', 'Club'),
    ('academic', 'Academic'),
    ('social', 'Social'),
    ('cultural', 'Cultural'),
    ('athletic', 'Athletic'),
    ('workshop', 'Workshop'),
]

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    CAMPUS_CHOICES = [
        ('main', 'Main Campus'),
        ('north', 'North Campus'),
        ('south', 'South Campus'),
        ('east', 'East Campus'),
        ('west', 'West Campus'),
        ('online', 'Online'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(default=time(12, 0))  # Default to noon
    location = models.CharField(max_length=200)
    campus = models.CharField(max_length=10, choices=CAMPUS_CHOICES, default='main')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    category = models.CharField(max_length=20, choices=EVENT_TYPES)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    def __str__(self):
        return self.title


class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], default='pending')

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
