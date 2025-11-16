from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from roles.models import Role
from .models import Jobs

User = get_user_model()


class JobViewSetTestCase(APITestCase):
    """Essential test cases for Jobs ViewSet."""

    def setUp(self):
        # Get or create default roles
        self.admin_role, _ = Role.objects.get_or_create(name='Administrator')
        self.recruiter_role, _ = Role.objects.get_or_create(name='Recruiter')
        self.evaluator_role, _ = Role.objects.get_or_create(name='Technical Evaluator')

        # Create users
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            password='testpass123',
            role=self.admin_role
        )
        self.recruiter_user = User.objects.create_user(
            email='recruiter@test.com',
            first_name='Recruiter',
            last_name='User',
            password='testpass123',
            role=self.recruiter_role
        )
        self.evaluator_user = User.objects.create_user(
            email='evaluator@test.com',
            first_name='Evaluator',
            last_name='User',
            password='testpass123',
            role=self.evaluator_role
        )

        # Create test job
        self.job = Jobs.objects.create(
            title='Python Developer',
            description='Python development position',
            employment_type='Full-time',
            location='New York',
            department='Engineering',
            experience_level='Mid',
            requirements='Python experience',
            posted_by_user_id=self.recruiter_user,
            status='Open'
        )

        self.list_url = reverse('jobs-list')
        self.detail_url = reverse('jobs-detail', kwargs={'pk': self.job.pk})

    def test_list_jobs(self):
        """Test listing jobs (public access)."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_job(self):
        """Test retrieving a Jobs (public access)."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Developer')

    def test_create_job_as_recruiter(self):
        """Test recruiter can create Jobs."""
        self.client.force_authenticate(user=self.recruiter_user)
        data = {
            'title': 'DevOps Engineer',
            'description': 'DevOps position',
            'employment_type': 'Full-time',
            'location': 'Remote',
            'department': 'Operations',
            'experience_level': 'Senior',
            'requirements': 'AWS, Docker',
            'posted_by_user_id': self.recruiter_user.id,
            'status': 'Open'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_job_as_evaluator_forbidden(self):
        """Test evaluator cannot create Jobs."""
        self.client.force_authenticate(user=self.evaluator_user)
        data = {
            'title': 'Test Job',
            'description': 'Test',
            'employment_type': 'Full-time',
            'location': 'Test',
            'department': 'Test',
            'experience_level': 'Entry',
            'requirements': 'Test',
            'status': 'Open'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_job_as_recruiter(self):
        """Test recruiter can update Jobs."""
        self.client.force_authenticate(user=self.recruiter_user)
        data = {'title': 'Senior Python Developer'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, 'Senior Python Developer')

    def test_update_job_as_evaluator_forbidden(self):
        """Test evaluator cannot update Jobs."""
        self.client.force_authenticate(user=self.evaluator_user)
        data = {'title': 'Hacked'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_job_as_admin(self):
        """Test admin can delete Jobs."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Jobs.objects.count(), 0)

    def test_delete_job_as_recruiter_forbidden(self):
        """Test recruiter cannot delete Jobs."""
        self.client.force_authenticate(user=self.recruiter_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
