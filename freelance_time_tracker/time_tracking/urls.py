from time_tracking.views import (
    StartTimeTrackingView, StopTimeTrackingView,
    ListInvoiveView, GenerateInvoiceView
)
from django.urls import path

app_name = "time_tracking"

urlpatterns = [
    path(
        'start/', StartTimeTrackingView.as_view(), name='start_time_tracking'
    ),
    path('stop/', StopTimeTrackingView.as_view(), name='stop_time_tracking'),
    path('invoices/', ListInvoiveView.as_view(), name='list_invoices'),
    path(
        'generate-invoice/',
        GenerateInvoiceView.as_view(),
        name='generate_invoice'
    ),
]
