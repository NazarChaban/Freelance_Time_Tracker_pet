from .models import TimeEntry, TimeTrackingLog
from rest_framework.response import Response
from rest_framework.views import APIView
from clients.models import Client
from rest_framework import status
from django.utils import timezone


class StartTimeTrackingView(APIView):
    """
    time-tracking/start/
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
