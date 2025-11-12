from django.urls import path

from rest_framework_simplejwt.views import (TokenRefreshView)
from . import views
urlpatterns = [
    path('token/', views.EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/logout/', views.LogoutView.as_view(), name='token_logout'),
]