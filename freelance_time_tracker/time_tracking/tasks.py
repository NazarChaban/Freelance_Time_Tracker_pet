from time_tracking.models import TimeEntry
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_incomplete_timesheet_reminders():
    threshold_time = timezone.now() - timezone.timedelta(hours=8)
    incomplete_entries = TimeEntry.objects.filter(
        end_time__isnull=True, start_time__lte=threshold_time
    )

    for entry in incomplete_entries:
        user = entry.user
        subject = "Reminder: Incomplete Timesheet Entry"
        message = (
            f"Hi, {user.username},\n\n"
            f"You have inncomplete timesheet with client {entry.client.name}, "
            f"that started {entry.start_time.strftime('%Y-%m-%d %H:%M:%S')}. "
            "Please close it.\n\n"
            "Thank you for your time!"
        )
        recipient_list = [user.email]

        try:
            send_mail(
                subject, message, settings.EMAIL_FROM,
                recipient_list, fail_silently=False
            )
            logger.info(
                f"Reminder sent to {user.email} "
                f"for timesheet with id {entry.id}"
            )
        except Exception as err:
            logger.exception(
                f"An error occured during sending email "
                f"to {user.email}: {str(err)}"
            )
            raise err
