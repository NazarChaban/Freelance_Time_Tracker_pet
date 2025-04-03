from rest_framework_simplejwt.views import TokenRefreshView
from users.views import SignupView, LoginView, LogoutView
from django.urls import path

app_name = 'api'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
