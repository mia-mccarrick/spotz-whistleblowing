from django.shortcuts import render
from django.views import generic
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
import boto3
from s3.models import Upload
from django.db import models
from django.db.models import Case, When
from django.contrib.auth import logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
class LoginView:
    template_name = "login/login_page.html"

def logout_view(request):
    logout(request)
    return home(request)
def home(request):
    if request.user.is_staff and not request.user.is_superuser:
        return staffpage(request)
    elif request.user.is_authenticated:
        return mainpage(request)
    else:
        return render(request, "login/home.html")
def mainpage(request):
    if request.user.is_authenticated:
        status_ordering = Case(
            When(status='New', then=0),
            When(status='In Progress', then=1),
            When(status='Resolved', then=2),
            default=0,
            output_field=models.IntegerField()
        )
        sort_by = request.GET.get('sort_by')
        if sort_by:
            request.session['sort_by'] = sort_by
        sort_by = request.session.get('sort_by', 'most_recent')
        if sort_by == 'most_recent':
            user_uploaded_files = Upload.objects.all().filter(user=request.user).order_by('-id')
        elif sort_by == 'not_yet_seen':
            user_uploaded_files = Upload.objects.all().filter(user=request.user).order_by(status_ordering, '-id')
        elif sort_by == 'priority':
            user_uploaded_files = Upload.objects.all().filter(user=request.user).order_by('-priority', status_ordering, '-id')
        elif sort_by == 'hide_resolved':
            user_uploaded_files = Upload.objects.all().filter(user=request.user).exclude(status="Resolved").order_by(status_ordering,'-priority', '-id')
        else:
            user_uploaded_files = Upload.objects.all().filter(user=request.user).order_by('-id')
        return render(request, 'login/mainpage.html', {'user_uploaded_files': user_uploaded_files, 'sort_by': sort_by})
    else:
        return render(request, 'login/mainpage.html', {})

def staffpage(request):
    if request.user.is_staff:
        status_ordering = Case(
            When(status='New', then=0),
            When(status='In Progress', then=1),
            When(status='Resolved', then=2),
            default=0,
            output_field=models.IntegerField()
        )
        sort_by = request.GET.get('sort_by')
        if sort_by:
            request.session['sort_by'] = sort_by
        sort_by = request.session.get('sort_by', 'most_recent')
        if sort_by == 'most_recent':
            all_uploaded_files = Upload.objects.all().order_by('-id')
        elif sort_by == 'not_yet_seen':
            all_uploaded_files = Upload.objects.all().order_by(status_ordering, '-id')
        elif sort_by == 'priority':
            all_uploaded_files = Upload.objects.all().order_by('-priority', status_ordering, '-id')
        elif sort_by == 'hide_resolved':
            all_uploaded_files = Upload.objects.all().exclude(status="Resolved").order_by(status_ordering, '-priority', '-id')

        return render(request, 'login/site-staff.html', {'all_uploaded_files': all_uploaded_files, 'sort_by': sort_by})
    else:
        return render(request, 'login/error.html')

def upload_admin_resolve(request, pk):
    uploaded_file = get_object_or_404(Upload, pk=pk)
    if (request.method == "POST"):
        uploaded_file.admin_comment = request.POST["comment"]
        uploaded_file.status = 'Resolved'
        uploaded_file.save()
        return redirect('login:staffpage')
    else:
        return render(request, 'login/error.html')

def change_priority(request, pk):
    uploaded_file = get_object_or_404(Upload, pk=pk)
    if (request.method == "POST"):
        uploaded_file.priority = request.POST["priority"]
        uploaded_file.save()
        return upload_detail(request, pk)
    else:
        return render(request, 'login/error.html')

def upload_detail(request, pk):
    uploaded_file = get_object_or_404(Upload, pk=pk)
    if request.user.is_authenticated == False or (uploaded_file.user != request.user and request.user.is_staff == False):
        return render(request, 'login/error.html')
    if uploaded_file.status == 'New' and request.user.is_staff:
        uploaded_file.status = 'In Progress'
        uploaded_file.save()
    return render(request, 'login/upload_detail.html', {'uploaded_file': uploaded_file})
def delete(request, pk):
    uploaded_file = get_object_or_404(Upload, pk=pk)
    if request.user.is_authenticated == False or (uploaded_file.user != request.user and request.user.is_staff == True):
        return render(request, 'login/error.html')
    uploaded_file.file.delete(save=False)
    uploaded_file.delete()
    return redirect('login:mainpage')
