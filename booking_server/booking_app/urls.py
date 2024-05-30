from django.urls import path
from . import views

urlpatterns = [
    path("userindex/",views.userindex,name="userindex")
]