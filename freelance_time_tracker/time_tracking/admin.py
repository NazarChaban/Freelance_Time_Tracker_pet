from time_tracking.models import (
    TimeEntry, TimeTrackingLog, Invoice, InvoiceTimeEntry
)
from django.contrib import admin

admin.site.register(TimeEntry)
admin.site.register(TimeTrackingLog)
admin.site.register(Invoice)
admin.site.register(InvoiceTimeEntry)
