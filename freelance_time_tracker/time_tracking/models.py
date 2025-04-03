from clients.models import Client
from django.conf import settings
from django.db import models
from decimal import Decimal


class TimeEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='time_entries'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='time_entries'
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None

    @property
    def earned_amount(self):
        if self.duration and self.client.rate:
            hours = Decimal(self.duration.total_seconds()) / Decimal(3600)
            return hours * self.client.rate
        return 0

    def __str__(self):
        return f"{self.user.username} - {self.client.name}" \
            f" ({self.start_time} - {self.end_time or 'in progress'})"


class TimeTrackingLog(models.Model):
    EVENT_CHOICES = (
        ('start', 'Start Tracking'),
        ('stop', 'Stop Tracking'),
        ('error', 'Error'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tracking_logs'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='tracking_logs',
        null=True,
        blank=True
    )
    time_entry = models.ForeignKey(
        TimeEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    event = models.CharField(max_length=10, choices=EVENT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} {self.get_event_display()} at {self.timestamp}"
