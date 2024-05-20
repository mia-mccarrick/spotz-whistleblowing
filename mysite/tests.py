import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from s3.models import Upload

class TestLoginApp():
    @pytest.mark.django_db
    def test_homepage_loading(self):
        client = Client()
        response = client.get(reverse('login:home'))
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_login_staff(self):
        client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345', is_staff=True)
        login = client.login(username='testuser', password='12345')
        response = client.get(reverse('login:staffpage'))
        assert login == True
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_login_user(self):
        client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345', is_staff=False)
        login = client.login(username='testuser', password='12345')
        response = client.get(reverse('login:mainpage'))
        assert login == True
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_login_admin(self):
        client = Client()
        self.user = User.objects.create_superuser('admin', password='12345678', is_staff=True)
        login = client.login(username='admin', password='12345678')
        response = client.get(reverse('login:mainpage'))
        assert login == True
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_upload_admin_resolve(self):
        client = Client()
        User.objects.create_user(username='staffuser', password='12345', is_staff=True)
        client.login(username='staffuser', password='12345')
        user = User.objects.create_user(username='testuser', password='12345', is_staff=False)
        uploaded_file = Upload.objects.create(user=user, status='New')
        response = client.post(reverse('login:admin_resolve', args=[uploaded_file.pk]),
                               {'comment': 'Resolved'})
        assert response.status_code == 302
        assert Upload.objects.get(pk=uploaded_file.pk).status == 'Resolved'

    @pytest.mark.django_db
    def test_change_priority(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='12345', is_staff=False)
        client.login(username='testuser', password='12345')

        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")
        uploaded_file = Upload.objects.create(user=user, status='New', file=txt_file)

        response = client.post(reverse('login:change_priority', args=[uploaded_file.pk]), {'priority': 2})
        assert response.status_code == 200
        updated_file = Upload.objects.get(pk=uploaded_file.pk)
        assert updated_file.priority == 2

    @pytest.mark.django_db
    def test_upload_detail(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='12345', is_staff=True)
        client.login(username='testuser', password='12345')

        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")
        uploaded_file = Upload.objects.create(user=user, status='New', file=txt_file)

        response = client.get(reverse('login:upload_detail', args=[uploaded_file.pk]))  # Simulate viewing upload detail
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_delete(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='12345', is_staff=False)
        client.login(username='testuser', password='12345')

        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")
        uploaded_file = Upload.objects.create(user=user, file=txt_file)

        response = client.post(reverse('login:delete', args=[uploaded_file.pk]))
        assert response.status_code == 302
        with pytest.raises(Upload.DoesNotExist):
            Upload.objects.get(pk=uploaded_file.pk)

    @pytest.mark.django_db
    def test_logout_view(self):
        client = Client()
        User.objects.create_user(username='testuser', password='12345')
        client.login(username='testuser', password='12345')
        client.get(reverse('login:logout'))
        assert '_auth_user_id' not in client.session

    @pytest.mark.django_db
    def test_mainpage_sorting_priority(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='12345')
        client.login(username='testuser', password='12345')

        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")

        Upload.objects.create(user=user, priority=3, status='New', file=txt_file)
        Upload.objects.create(user=user, priority=1, status='New', file=txt_file)
        Upload.objects.create(user=user, priority=2, status='New', file=txt_file)

        response = client.get(reverse('login:mainpage') + '?sort_by=priority')
        sorted_files = response.context['user_uploaded_files']
        assert sorted_files.count() == 3
        assert sorted_files[0].priority == 3
        assert sorted_files[1].priority == 2
        assert sorted_files[2].priority == 1

    @pytest.mark.django_db
    def test_mainpage_sorting_status(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='12345')
        client.login(username='testuser', password='12345')

        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")

        Upload.objects.create(user=user, priority=1, status='In Progress', file=txt_file)
        Upload.objects.create(user=user, priority=1, status='New', file=txt_file)
        Upload.objects.create(user=user, priority=1, status='Resolved', file=txt_file)

        response = client.get(reverse('login:mainpage') + '?sort_by=not_yet_seen')
        sorted_files = response.context['user_uploaded_files']
        assert sorted_files.count() == 3
        assert sorted_files[0].status == "New"
        assert sorted_files[1].status == "In Progress"
        assert sorted_files[2].status == "Resolved"

    @pytest.mark.django_db
    def test_mainpage_sorting_most_recent(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='12345')
        client.login(username='testuser', password='12345')

        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")

        Upload.objects.create(user=user, priority=3, status='In Progress', file=txt_file)
        Upload.objects.create(user=user, priority=2, status='New', file=txt_file)
        Upload.objects.create(user=user, priority=1, status='Resolved', file=txt_file)

        response = client.get(reverse('login:mainpage') + '?sort_by=most_recent')
        sorted_files = response.context['user_uploaded_files']
        assert sorted_files.count() == 3
        assert sorted_files[0].priority == 1
        assert sorted_files[1].priority == 2
        assert sorted_files[2].priority == 3

    @pytest.mark.django_db
    def test_mainpage_hide_resolved(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='12345')
        client.login(username='testuser', password='12345')

        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")

        Upload.objects.create(user=user, priority=3, status='In Progress', file=txt_file)
        Upload.objects.create(user=user, priority=2, status='New', file=txt_file)
        Upload.objects.create(user=user, priority=1, status='Resolved', file=txt_file)

        response = client.get(reverse('login:mainpage') + '?sort_by=hide_resolved')
        sorted_files = response.context['user_uploaded_files']
        assert sorted_files.count() == 2
        assert sorted_files[0].priority == 2
        assert sorted_files[1].priority == 3

    @pytest.mark.django_db
    def test_mainpage_sorting_priority_staff(self):
        client = Client()
        user1 = User.objects.create_user(username='testuser1', password='12345')
        user2 = User.objects.create_user(username='testuser2', password='12345')
        user3 = User.objects.create_user(username='testuser3', password='12345')

        User.objects.create_user(username='staffuser', password='12345678', is_staff=True)
        client.login(username='staffuser', password='12345678')

        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")

        Upload.objects.create(user=user1, priority=3, status='New', file=txt_file)
        Upload.objects.create(user=user2, priority=1, status='New', file=txt_file)
        Upload.objects.create(user=user3, priority=2, status='New', file=txt_file)

        response = client.get(reverse('login:staffpage') + '?sort_by=priority')
        sorted_files = response.context['all_uploaded_files']
        assert sorted_files.count() == 3
        assert sorted_files[0].priority == 3
        assert sorted_files[1].priority == 2
        assert sorted_files[2].priority == 1

    @pytest.mark.django_db
    def test_mainpage_sorting_status_staff(self):
        client = Client()
        user1 = User.objects.create_user(username='testuser1', password='12345')
        user2 = User.objects.create_user(username='testuser2', password='12345')
        user3 = User.objects.create_user(username='testuser3', password='12345')

        User.objects.create_user(username='staffuser', password='12345678', is_staff=True)
        client.login(username='staffuser', password='12345678')

        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")

        Upload.objects.create(user=user1, priority=1, status='In Progress', file=txt_file)
        Upload.objects.create(user=user2, priority=1, status='New', file=txt_file)
        Upload.objects.create(user=user3, priority=1, status='Resolved', file=txt_file)

        response = client.get(reverse('login:staffpage') + '?sort_by=not_yet_seen')
        sorted_files = response.context['all_uploaded_files']
        assert sorted_files.count() == 3
        assert sorted_files[0].status == "New"
        assert sorted_files[1].status == "In Progress"
        assert sorted_files[2].status == "Resolved"

    @pytest.mark.django_db
    def test_mainpage_sorting_most_recent_staff(self):
        client = Client()
        user1 = User.objects.create_user(username='testuser1', password='12345')
        user2 = User.objects.create_user(username='testuser2', password='12345')
        user3 = User.objects.create_user(username='testuser3', password='12345')

        User.objects.create_user(username='staffuser', password='12345678', is_staff=True)
        client.login(username='staffuser', password='12345678')
        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")

        Upload.objects.create(user=user1, priority=3, status='In Progress', file=txt_file)
        Upload.objects.create(user=user2, priority=2, status='New', file=txt_file)
        Upload.objects.create(user=user3, priority=1, status='Resolved', file=txt_file)

        response = client.get(reverse('login:staffpage') + '?sort_by=most_recent')
        sorted_files = response.context['all_uploaded_files']
        assert sorted_files.count() == 3
        assert sorted_files[0].priority == 1
        assert sorted_files[1].priority == 2
        assert sorted_files[2].priority == 3

    @pytest.mark.django_db
    def test_mainpage_hide_resolved_staff(self):
        client = Client()
        user1 = User.objects.create_user(username='testuser1', password='12345')
        user2 = User.objects.create_user(username='testuser2', password='12345')
        user3 = User.objects.create_user(username='testuser3', password='12345')

        User.objects.create_user(username='staffuser', password='12345678', is_staff=True)
        client.login(username='staffuser', password='12345678')
        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")

        Upload.objects.create(user=user1, priority=3, status='In Progress', file=txt_file)
        Upload.objects.create(user=user2, priority=2, status='New', file=txt_file)
        Upload.objects.create(user=user3, priority=1, status='Resolved', file=txt_file)

        response = client.get(reverse('login:staffpage') + '?sort_by=hide_resolved')
        sorted_files = response.context['all_uploaded_files']
        assert sorted_files.count() == 2
        assert sorted_files[0].priority == 2
        assert sorted_files[1].priority == 3

    @pytest.mark.django_db
    def test_resolve_changes_color_staff(self):
        client = Client()
        user = User.objects.create_user(username='staffuser', password='12345', is_staff=True)
        client.login(username='staffuser', password='12345')
        uploaded_file = Upload.objects.create(user=user, status='New')
        response = client.post(reverse('login:admin_resolve', args=[uploaded_file.pk]), {'comment': 'Resolved'})

        assert response.status_code == 302
        resolved_file = Upload.objects.get(pk=uploaded_file.pk)
        assert resolved_file.status == 'Resolved'

        response = client.get(reverse('login:staffpage'))
        assert response.status_code == 200
        assert '<div class="upload-module resolved"' in str(response.content)

    @pytest.mark.django_db
    def test_resolve_changes_color_regular(self):
        client = Client()
        user = User.objects.create_user(username='reguser', password='12345', is_staff=False)
        client.login(username='reguser', password='12345')

        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")
        Upload.objects.create(user=user, priority=3, status='Resolved', file=txt_file)

        response = client.get(reverse('login:mainpage'))
        assert response.status_code == 200
        assert '<div class="upload-module resolved"' in str(response.content)

    @pytest.mark.django_db
    def test_new_upload_has_icon(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='12345', is_staff=True)
        client.login(username='testuser', password='12345')
        Upload.objects.create(user=user, status='New')
        response = client.get(reverse('login:staffpage'))
        assert response.status_code == 200
        assert '<img class="new-status-image"' in str(response.content)

    @pytest.mark.django_db
    def test_delete_redirect(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='12345', is_staff=False)
        client.login(username='testuser', password='12345')

        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")
        uploaded_file = Upload.objects.create(user=user, file=txt_file)

        response = client.post(reverse('login:delete', args=[uploaded_file.pk]))
        assert response.url == reverse('login:mainpage')

    @pytest.mark.django_db
    def test_resolve_redirect(self):
        client = Client()
        User.objects.create_user(username='staffuser', password='12345', is_staff=True)
        client.login(username='staffuser', password='12345')
        user = User.objects.create_user(username='testuser', password='12345', is_staff=False)
        uploaded_file = Upload.objects.create(user=user, status='New')
        response = client.post(reverse('login:admin_resolve', args=[uploaded_file.pk]),
                               {'comment': 'Resolved'})
        assert response.url == reverse('login:staffpage')

    @pytest.mark.django_db
    #test underlying sort, after priority
    def test_sorting_priority_mixed_staff(self):
        client = Client()
        user1 = User.objects.create_user(username='testuser1', password='12345')
        user2 = User.objects.create_user(username='testuser2', password='12345')
        user3 = User.objects.create_user(username='testuser3', password='12345')

        User.objects.create_user(username='staffuser', password='12345678', is_staff=True)
        client.login(username='staffuser', password='12345678')

        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")

        Upload.objects.create(user=user1, priority=3, status='New', file=txt_file)
        Upload.objects.create(user=user2, priority=1, status='New', file=txt_file)
        Upload.objects.create(user=user2, priority=1, status='In Progress', file=txt_file)
        Upload.objects.create(user=user3, priority=2, status='New', file=txt_file)

        response = client.get(reverse('login:staffpage') + '?sort_by=priority')
        sorted_files = response.context['all_uploaded_files']
        assert sorted_files.count() == 4
        assert sorted_files[0].priority == 3
        assert sorted_files[1].priority == 2
        assert sorted_files[2].priority == 1
        assert sorted_files[3].status == "In Progress"

    @pytest.mark.django_db
    def test_priority_icon_new(self):
        client = Client()
        user = User.objects.create_user(username='staffuser', password='12345', is_staff=True)
        client.login(username='staffuser', password='12345')
        Upload.objects.create(user=user, status='New', priority=4)
        response = client.get(reverse('login:staffpage'))
        assert response.status_code == 200
        assert 'src="../../static/images/new-high.jpg"' in str(response.content)

    @pytest.mark.django_db
    def test_priority_icon_resolved(self):
        client = Client()
        user = User.objects.create_user(username='staffuser', password='12345', is_staff=True)
        client.login(username='staffuser', password='12345')
        Upload.objects.create(user=user, status='Resolved', priority=1)
        response = client.get(reverse('login:staffpage'))
        assert response.status_code == 200
        assert 'src="../../static/images/res-lowest.jpg"' in str(response.content)

    @pytest.mark.django_db
    def test_file_upload(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='12345')
        client.login(username='testuser', password='12345')
        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")
        uploaded_file = Upload.objects.create(user=user, file=txt_file)
        response = client.post(reverse('s3:submit'), {'file': uploaded_file})
        assert response.url == reverse('login:mainpage')
