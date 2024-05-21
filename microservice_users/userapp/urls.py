from django.urls import path
from . import views 

urlpatterns=[
    path('',views.index,name='index'),
    path('registration/',views.registration,name='registration'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('management/',views.management,name='management'),
    path('createdoctor/',views.createdoctor,name='createdoctor'),
]