from django.urls import path
from . import views

urlpatterns = [
    path("userindex/",views.userindex,name="userindex"),
    path("book_appointment/",views.book_appointment,name="book_appointment"),
    path("get_doctor_schedule/",views.get_doctor_schedule,name="get_doctor_schedule")
]