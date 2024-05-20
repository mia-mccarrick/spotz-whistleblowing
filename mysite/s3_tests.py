import pytest
from django.urls import reverse
from django.test import Client, TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import boto3
from botocore.stub import Stubber
from s3.models import Upload
import io
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile


class TestUpload():
    @pytest.fixture
    def s3_stubber(self):
        with Stubber(boto3.client("s3")) as stubber:
            yield stubber
    @pytest.mark.django_db
    def test_submit_pdf_and_verify_success_page(self, s3_stubber):
        client = Client()
        pdf_content = b"Testing pdf content"
        pdf_file = SimpleUploadedFile("file.pdf", pdf_content, content_type="application/pdf")

        s3_stubber.add_response('put_object', {}, expected_params={
            'Bucket': 'spotz',
            'Key': 'file.pdf',
            'Body': pdf_content,
            'ContentType': 'application/pdf'
        })

        with s3_stubber:
            response = client.post(reverse("s3:submission_page"), {"file": pdf_file})
        assert response.status_code == 200
    @pytest.mark.django_db
    def test_submit_image_and_verify_success_page(self, s3_stubber):
        client = Client()
        img_content = b"Testing image content"
        jpg_file = SimpleUploadedFile("img.jpg", img_content, content_type="application/jpg")

        s3_stubber.add_response('put_object', {}, expected_params={
            'Bucket': 'spotz',
            'Key': 'img.jpg',
            'Body': img_content,
            'ContentType': 'application/jpg'
        })

        with s3_stubber:
            response = client.post(reverse("s3:submission_page"), {"file": jpg_file})
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_submit_text_and_verify_success_page(self, s3_stubber):
        client = Client()
        txt_content = b"Testing text file content"
        txt_file = SimpleUploadedFile("file.txt", txt_content, content_type="application/txt")

        s3_stubber.add_response('put_object', {}, expected_params={
            'Bucket': 'spotz',
            'Key': 'file.txt',
            'Body': txt_content,
            'ContentType': 'application/txt'
        })

        with s3_stubber:
            response = client.post(reverse("s3:submission_page"), {"file": txt_file})
        assert response.status_code == 200

class UploadModelTestCase(TestCase):
    @pytest.mark.django_db
    def test_valid_mime_type(self):
        pdf_content = b"%PDF-1.4\n..."
        pdf_file = InMemoryUploadedFile(
            io.BytesIO(pdf_content),
            None,
            "test.pdf",
            "application/pdf",
            len(pdf_content),
            None
        )
        try:
            Upload.validate_mime_type(pdf_file)
        except ValidationError:
            self.fail("validate_mime_type raised ValidationError unexpectedly")

    @pytest.mark.django_db
    def test_invalid_mime_type(self):
        zip_content = b"PK\x03\x04\n..."
        zip_file = InMemoryUploadedFile(
            io.BytesIO(zip_content),
            None,
            "test.zip",
            "application/zip",
            len(zip_content),
            None
        )
        with self.assertRaises(ValidationError):
            Upload.validate_mime_type(zip_file)

    @pytest.mark.django_db
    def test_file_too_large(self):
        large_content = b"A" * (1024 * 1024 * 11)
        large_file = InMemoryUploadedFile(
            io.BytesIO(large_content),
            None,
            "large_file.txt",
            "text/plain",
            len(large_content),
            None
        )
        with self.assertRaises(ValidationError):
            Upload.validate_mime_type(large_file)