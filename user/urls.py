from django.urls import path
from .views import Join, Login, LogOut, UploadProfile, Follow, ViewFollow

urlpatterns = [
    path('join', Join.as_view()),
    path('login', Login.as_view()),
    path('logout', LogOut.as_view()),
    path('profile/upload', UploadProfile.as_view()),
    path('<str:username>/follow', Follow.as_view()),
    path('view_follow/', ViewFollow.as_view())
]
