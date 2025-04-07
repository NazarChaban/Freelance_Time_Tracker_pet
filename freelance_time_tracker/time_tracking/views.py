from time_tracking.models import (
    TimeEntry, TimeTrackingLog, Invoice, InvoiceTimeEntry
)
from rest_framework.response import Response
from rest_framework.views import APIView
from clients.models import Client
from rest_framework import status
from django.utils import timezone


class StartTimeTrackingView(APIView):
    """
    time-tracking/start/?client_id=<client_id>
    """
    def post(self, request):
        client_id = request.data.get('client_id')

        if not client_id:
            return Response(
                {"detail": "client_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            client = Client.objects.get(id=client_id, user=request.user)
        except Client.DoesNotExist:
            return Response(
                {"detail": "client not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not client.is_active:
            return Response(
                {"detail": "client is inactive"},
                status=status.HTTP_400_BAD_REQUEST
            )

        active_entry = TimeEntry.objects.filter(
            user=request.user, end_time__isnull=True
        ).first()
        if active_entry:
            return Response(
                {"detail": "You are already tracking time"},
                status=status.HTTP_400_BAD_REQUEST
            )

        time_entry = TimeEntry.objects.create(user=request.user, client=client)
        TimeTrackingLog.objects.create(
            user=request.user,
            client=client,
            time_entry=time_entry,
            event='start',
            details=(
                "Started tracking time for user - "
                f"{request.user.username} and client - {client.name}"
            )
        )

        return Response(
            {
                "detail": "Time tracking started.",
                "start_time": time_entry.start_time,
            },
            status=status.HTTP_201_CREATED
        )


class StopTimeTrackingView(APIView):
    """
    time-tracking/stop/
    """
    def post(self, request):
        user = request.user
        time_entry = TimeEntry.objects.filter(
            user=user, end_time__isnull=True
        ).first()
        if not time_entry:
            return Response(
                {"detail": "No active time tracking found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        client = time_entry.client

        time_entry.end_time = timezone.now()
        time_entry.save()

        details = f"Stopped tracking for user - {user.username} " \
            f"and client - {client.name}; " \
            f"duration: {time_entry.duration}."
        TimeTrackingLog.objects.create(
            user=user,
            client=client,
            time_entry=time_entry,
            event='stop',
            details=details
        )

        invoice, _ = Invoice.objects.get_or_create(
            user=user,
            client=client,
            done=False
        )

        InvoiceTimeEntry.objects.create(
            invoice=invoice,
            time_entry=time_entry
        )

        duration = 0
        if time_entry.duration:
            duration = time_entry.duration.total_seconds()

        return Response(
            {
                "detail": "Time tracking stopped",
                "start_time": time_entry.start_time,
                "end_time": time_entry.end_time,
                "duration_seconds": duration,
                "earned_amount": time_entry.earned_amount
            },
            status=status.HTTP_200_OK
        )


def format_time(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


class ListInvoiveView(APIView):
    """
    time-tracking//invoices/
    time-tracking//invoices/?client_id=<client_id>
    time-tracking//invoices/?invoice_id=<invoice_id>
    """
    def get(self, request):
        invoices = Invoice.objects.filter(user=request.user, done=True)
        client_id = request.query_params.get('client_id')
        invoice_id = request.query_params.get('invoice_id')

        if client_id:
            invoices = invoices.filter(client_id=client_id)
        if invoice_id:
            invoices = invoices.filter(id=invoice_id)

        if not invoices.exists():
            return Response(
                {"detail": "Invoices not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        invoice_data = [
            {
                "id": invoice.id,
                "client": invoice.client.name,
                "issued_at": invoice.issued_at,
                "total_time_seconds": invoice.total_time,
                "total_time": format_time(invoice.total_time.total_seconds()),
                "total_amount": invoice.total_amount,
                "invoice_file": invoice.invoice_file.url
            } for invoice in invoices
        ]
        return Response(
            invoice_data,
            status=status.HTTP_200_OK
        )


class GenerateInvoiceView(APIView):
    """
    time-tracking/generate-invoice/?client_id=<client_id>
    """
    def post(self, request):
        client_id = request.data.get('client_id')
        if not client_id:
            return Response(
                {"detail": "client_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            invoice = Invoice.objects.get(
                user=request.user, client_id=client_id, done=False
            )
        except Invoice.DoesNotExist:
            return Response(
                {"detail": "No open invoices for this client"},
                status=status.HTTP_404_NOT_FOUND
            )

        invoice.generate_invoice()
        return Response({
            "detail": "Invoice generated",
            "id": invoice.id,
            "client": invoice.client.name,
            "total_time_seconds": invoice.total_time.total_seconds(),
            "total_amount": invoice.total_amount,
            "invoice_file": invoice.invoice_file.url
        }, status=status.HTTP_200_OK)
