from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('application-statuses', views.ApplicationStatusesViewSet, basename='applicationstatuses')

urlpatterns = [
    path('', include(router.urls)),
]