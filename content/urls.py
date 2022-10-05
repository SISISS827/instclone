from django.urls import path
from .views import UploadFeed, Profile, Main, UploadReply, ToggleLike, ToggleBookmark
from . import views

urlpatterns = [
    path('upload', UploadFeed.as_view()),
    path('reply', UploadReply.as_view()),
    path('like', ToggleLike.as_view()),
    path('bookmark', ToggleBookmark.as_view()),
    path('profile', Profile.as_view()),
    path('<int:pk>/delete/', views.feed_delete),
    path('<int:pk>/update/', views.feed_update),
]