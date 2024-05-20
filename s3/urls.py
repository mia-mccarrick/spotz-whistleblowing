from django.urls import path
from . import views

app_name = "s3"
urlpatterns = [
    path("", views.UploadCreateView.as_view(), name="submission_page"),
    path("submit", views.submit, name="submit"),
]