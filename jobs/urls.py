from django.urls import path ,include

from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('jobs',views.JobViewset,basename='jobs')
urlpatterns = [
    path("",include(router.urls))
]