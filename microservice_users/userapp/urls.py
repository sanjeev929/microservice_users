from django.urls import path
from . import views 

urlpatterns=[
    path('',views.index,name='index'),
    path('registration/',views.registration,name='registration'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('management/',views.management,name='management'),
    path('createdoctor/',views.createdoctor,name='createdoctor'),
    path('doctorsetpassword/',views.doctorsetpassword,name='doctorsetpassword'),
    path('editdoctor/',views.editdoctor,name="editdoctor"),
    path('deletedoctor/',views.deletedoctor,name="deletedoctor"),
    path('book_appointment/',views.book_appointment,name="book_appointment"),
    path('appointment/',views.appointment,name="appointment"),
    path('doctorindex/',views.doctorindex,name="doctorindex"),
    path('approved/',views.approved,name="approved"),
    path('endmeet/',views.endmeet,name="endmeet"),

]