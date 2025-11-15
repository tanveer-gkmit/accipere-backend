from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from roles.models import Role
from .models import ApplicationStatuses

User = get_user_model()


class ApplicationStatusesViewSetTestCase(APITestCase):
    """Essential test cases for ApplicationStatuses ViewSet."""

    def setUp(self):
        # Create roles
        self.admin_role, _ = Role.objects.get_or_create(name='Administrator')
        self.recruiter_role, _ = Role.objects.get_or_create(name='Recruiter')

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

        # Create test statuses
        ApplicationStatuses.objects.all().delete()
        self.statuses = []
        for index, status_name in enumerate(["HR Screening", "Technical Screening", "Interview", "Rejected"]):
            status_obj = ApplicationStatuses.objects.create(
                name=status_name,
                description=status_name,
                order_sequence=index
            )
            self.statuses.append(status_obj)

        self.list_url = '/api/application-statuses/'
        self.detail_url = f'/api/application-statuses/{self.statuses[0].pk}/'
        self.reorder_url = '/api/application-statuses/reorder/'

    def test_list_statuses_authenticated(self):
        """Test authenticated user can list statuses."""
        self.client.force_authenticate(user=self.recruiter_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)

    def test_list_statuses_unauthenticated(self):
        """Test unauthenticated user cannot list statuses."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_status_as_admin(self):
        """Test admin can create status."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Final Interview', 'description': 'Final round'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Final Interview')

    def test_create_status_as_non_admin(self):
        """Test non-admin cannot create status."""
        self.client.force_authenticate(user=self.recruiter_user)
        data = {'name': 'New Status', 'description': 'Test'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_status_as_admin(self):
        """Test admin can update status."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'description': 'Updated description'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')

    def test_update_status_as_non_admin(self):
        """Test non-admin cannot update status."""
        self.client.force_authenticate(user=self.recruiter_user)
        data = {'description': 'Hacked'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_status_as_admin(self):
        """Test admin can delete status."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ApplicationStatuses.objects.count(), 3)

    def test_delete_status_as_non_admin(self):
        """Test non-admin cannot delete status."""
        self.client.force_authenticate(user=self.recruiter_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reorder_statuses_as_admin(self):
        """Test admin can reorder statuses."""
        self.client.force_authenticate(user=self.admin_user)
        items = [
            {'id': self.statuses[1].id, 'order_sequence': 0},
            {'id': self.statuses[0].id, 'order_sequence': 1},
        ]
        data = {'items': items}
        response = self.client.post(self.reorder_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reorder_statuses_as_non_admin(self):
        """Test non-admin cannot reorder statuses."""
        self.client.force_authenticate(user=self.recruiter_user)
        items = [{'id': self.statuses[0].id, 'order_sequence': 1}]
        data = {'items': items}
        response = self.client.post(self.reorder_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
