from django.urls import path
from .view import Login, Logout
urlpatterns = [
    path('', Login.as_view(), name='LOGIN'),
    path('logout/', Logout.as_view(), name='LOGOUT'),
]