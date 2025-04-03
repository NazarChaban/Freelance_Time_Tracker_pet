from time_tracking.views import StartTimeTrackingView, StopTimeTrackingView
from django.urls import path

app_name = "time_tracking"

urlpatterns = [
    path(
        'start/', StartTimeTrackingView.as_view(), name='start_time_tracking'
    ),
    path('stop/', StopTimeTrackingView.as_view(), name='stop_time_tracking'),
]
