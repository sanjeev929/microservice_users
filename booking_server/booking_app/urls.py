from django.urls import path
from . import views

urlpatterns = [
    path("userindex/",views.userindex,name="userindex"),
    path("book_appointment/",views.book_appointment,name="book_appointment"),
    path("get_doctor_schedule/",views.get_doctor_schedule,name="get_doctor_schedule"),
    path("get_schedule_status/",views.get_schedule_status,name="get_schedule_status"),
    path("doctor_index/",views.doctor_index,name="doctor_index"),
    path("status_change/",views.status_change,name="status_change"),
    path("doctor_approved/",views.doctor_approved,name="doctor_approved"),
    path("create_meeting/",views.create_meeting,name="create_meeting"),
    path("endmeeting/",views.endmeeting,name="endmeeting"),
    path("management/",views.management,name="management"),
    path("dashboard/",views.dashboard,name="dashboard"),
]