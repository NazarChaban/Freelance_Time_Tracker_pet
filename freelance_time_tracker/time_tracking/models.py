from django.core.files.base import ContentFile
from django.utils.text import slugify
from clients.models import Client
from django.utils import timezone
from django.conf import settings
from django.db import models
from decimal import Decimal
from io import StringIO
import csv
import os


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


def invoice_upload_filepath(instance, filename):
    """
    Generate path to invoice file in format:
    Invoices/<username>_invoices/<client_name>_invoices/<filename>
    """
    username = slugify(instance.user.username)
    client_name = slugify(instance.client.name)
    user_directory = f"{username}_invoices"
    client_directory = f"{client_name}_invoices"
    return os.path.join(
        "Invoices", user_directory, client_directory, filename
    )


class Invoice(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    total_time = models.DurationField(null=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    done = models.BooleanField(default=False)
    issued_at = models.DateTimeField(auto_now_add=True)
    invoice_file = models.FileField(
        upload_to=invoice_upload_filepath, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def get_time_entries(self):
        time_entries = [
            entry.time_entry for entry in self.invoice_entries.all()
            if entry.time_entry.end_time is not None
        ]
        return time_entries

    def get_totals(self, time_entries):
        total_seconds = sum(
            [
                te.duration.total_seconds() for te in time_entries
                if te.duration
            ]
        )
        total_time = timezone.timedelta(seconds=total_seconds)
        total_amount = sum([te.earned_amount for te in time_entries])
        return total_time, total_amount

    def generate_invoice(self):
        time_entries = self.get_time_entries()

        self.total_time, self.total_amount = self.get_totals(time_entries)
        self.done = True
        self.save()

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["start_time", "end_time", "duration", "rate", "money_earned"]
        )
        for te in time_entries:
            writer.writerow([
                te.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                te.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                str(te.duration),
                te.client.rate,
                te.earned_amount
            ])
        content = output.getvalue()
        output.close()
        self.invoice_file.save(f"invoice_{self.id}.csv", ContentFile(content))
        self.save()

    def __str__(self):
        return f"Invoice {self.id} for {self.client} ({self.issued_at.date()})"


class InvoiceTimeEntry(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='invoice_entries'
    )
    time_entry = models.ForeignKey(
        TimeEntry,
        on_delete=models.CASCADE,
        related_name='invoice_entries'
    )

    class Meta:
        unique_together = ('invoice', 'time_entry')

    def __str__(self):
        return f"Invoice {self.invoice.id} - TimeEntry {self.time_entry.id}"
