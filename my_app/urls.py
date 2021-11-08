from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home),
    path('login/', views.login),
    path('login/logic/', views.login_logic),
    path('register/', views.register),
    path('register/logic/', views.register_logic),
    path('plagiarism/', views.post_upload),
    path('addfile/', views.add_file),
]
