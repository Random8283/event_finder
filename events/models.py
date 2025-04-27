from django.db import models
from django.contrib.auth.models import User
from datetime import date, time
from PIL import Image

# Create your models here.

class Event(models.Model):
    CAMPUS_CHOICES = [
        ('main', 'Main Campus'),
        ('north', 'North Campus'),
        ('south', 'South Campus'),
        ('east', 'East Campus'),
        ('west', 'West Campus'),
        ('online', 'Online'),
    ]
    EVENT_TYPES = [
        ('club', 'Club'),
        ('academic', 'Academic'),
        ('social', 'Social'),
        ('cultural', 'Cultural'),
        ('athletic', 'Athletic'),
        ('workshop', 'Workshop'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(default=time(12, 0))  # Default to noon
    location = models.CharField(max_length=200)
    campus = models.CharField(max_length=10, choices=CAMPUS_CHOICES, default='main')
    category = models.CharField(max_length=10, choices=EVENT_TYPES, default='main')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)

            # Resize the image to a fixed size (e.g., 300x300 pixels)
            output_size = (300, 300)
            img = img.resize(output_size, Image.Resampling.LANCZOS)  # Updated here
            img.save(self.image.path)

    @property
    def is_past_event(self):
        """Check if the event date is in the past."""
        return self.date < date.today()

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
