from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from .forms import UploadForm
from .models import Upload
from django.urls import reverse_lazy
from django.views.generic import View
from django.contrib import messages


class UploadCreateView(CreateView):
    model = Upload
    form_class = UploadForm
    success_url = reverse_lazy("s3:submit")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uploads = Upload.objects.all()
        context['uploads'] = uploads
        return context

    # We used an example from the following site for this view: https://simpleisbetterthancomplex.com/tutorial/2017/08/01/how-to-setup-amazon-s3-in-a-django-project.html

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        return super().form_valid(form)

def submit(request):
    return redirect('login:mainpage')

