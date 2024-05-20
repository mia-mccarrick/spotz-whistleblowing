from allauth.account.views import LoginView
from django.urls import path
from . import views

app_name = "login"
urlpatterns = [
    #path("", LoginView.as_view(), name="login"),
    path("", views.home, name="home"),
    path("mainpage", views.mainpage, name="mainpage"),
    path("site-staff", views.staffpage, name="staffpage"),
    path("upload/<int:pk>/", views.upload_detail, name="upload_detail"),
    path("upload/<int:pk>/admin_resolve", views.upload_admin_resolve, name="admin_resolve"),
    path("logout", views.logout_view, name="logout"),
    path("upload/<int:pk>/delete", views.delete, name="delete"),
    path("upload/<int:pk>/change_priority", views.change_priority, name="change_priority"),
]
