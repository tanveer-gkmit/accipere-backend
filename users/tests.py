from django.test import TestCase
from django.contrib.auth import get_user_model
from roles.models import Role
from rest_framework.test import APITestCase
from rest_framework import status as http_status
from applications.models import Applications, ApplicationStatuses, ApplicationAssignedUserStatuses
from jobs.models import Jobs
User = get_user_model()


class UserManagerTestCase(TestCase):
    """Test cases for UserManager"""
    
    def setUp(self):
        """Set up test data"""
        self.role, _ = Role.objects.get_or_create(name='Recruiter', defaults={'description': 'Recruiter role'})
        self.admin_role, _ = Role.objects.get_or_create(name='Administrator', defaults={'description': 'Administrator role'})
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123',
            role=self.role
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_user_without_email(self):
        """Test creating user without email raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                first_name='Test',
                last_name='User',
                password='testpass123',
                role=self.role
            )
    
    def test_create_user_without_first_name(self):
        """Test creating user without first name raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='test@example.com',
                first_name='',
                last_name='User',
                password='testpass123',
                role=self.role
            )
    
    def test_create_user_without_last_name(self):
        """Test creating user without last name raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='test@example.com',
                first_name='Test',
                last_name='',
                password='testpass123',
                role=self.role
            )
    
    def test_create_superuser(self):
        """Test creating a superuser automatically gets Administrator role"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='adminpass123'
        )
        
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role.name, 'Administrator')
    
    def test_create_superuser_with_is_staff_false(self):
        """Test creating superuser with is_staff=False raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                password='adminpass123',
                is_staff=False
            )
    
    def test_create_superuser_with_is_superuser_false(self):
        """Test creating superuser with is_superuser=False raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                password='adminpass123',
                is_superuser=False
            )
    
    def test_create_superuser_with_non_administrator_role(self):
        """Test creating superuser with non-Administrator role raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                password='adminpass123',
                role=self.role
            )

class UserApplicationsEndpointTestCase(APITestCase):
    """Test cases for GET /api/users/{id}/applications/ endpoint"""
    
    def setUp(self):
        """Set up test data"""
        # Create roles
        self.admin_role, _ = Role.objects.get_or_create(name='Administrator', defaults={'description': 'Administrator role'})
        self.recruiter_role, _ = Role.objects.get_or_create(name='Recruiter', defaults={'description': 'Recruiter role'})
        
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
        self.another_recruiter = User.objects.create_user(
            email='recruiter2@test.com',
            first_name='Another',
            last_name='Recruiter',
            password='testpass123',
            role=self.recruiter_role
        )
        
        # Create application statuses (use get_or_create to avoid conflicts)
        self.status_screening, _ = ApplicationStatuses.objects.get_or_create(
            name='Screening',
            defaults={
                'description': 'Initial screening',
                'order_sequence': 1
            }
        )
        self.status_interview, _ = ApplicationStatuses.objects.get_or_create(
            name='Interview',
            defaults={
                'description': 'Interview stage',
                'order_sequence': 2
            }
        )
        self.status_rejected, _ = ApplicationStatuses.objects.get_or_create(
            name='Rejected',
            defaults={
                'description': 'Rejected',
                'order_sequence': 3
            }
        )
        
        # Create a job
        self.job = Jobs.objects.create(
            title='Software Engineer',
            description='Test job',
            department='Engineering',
            location='Remote',
            employment_type='Full-time',
            experience_level='Mid',
            requirements='Python, Django',
            salary_min=80000,
            salary_max=120000,
            status='Open'
        )
        
        # Create applications
        self.app1 = Applications.objects.create(
            job_id=self.job,
            email='candidate1@test.com',
            phone_no='9876543210',
            first_name='Candidate',
            last_name='One',
            resume=b'fake_pdf_content',
            street='123 Main St',
            city='Mumbai',
            zip_code='400001',
            current_status=self.status_screening
        )
        
        self.app2 = Applications.objects.create(
            job_id=self.job,
            email='candidate2@test.com',
            phone_no='9876543211',
            first_name='Candidate',
            last_name='Two',
            resume=b'fake_pdf_content',
            street='456 Oak St',
            city='Delhi',
            zip_code='110001',
            current_status=self.status_interview
        )
        
        self.app3 = Applications.objects.create(
            job_id=self.job,
            email='candidate3@test.com',
            phone_no='9876543212',
            first_name='Candidate',
            last_name='Three',
            resume=b'fake_pdf_content',
            street='789 Pine St',
            city='Bangalore',
            zip_code='560001',
            current_status=self.status_screening
        )
        
        # Assign applications to recruiter_user
        # App1: assigned to screening status (matches current_status)
        ApplicationAssignedUserStatuses.objects.create(
            application_id=self.app1,
            status_id=self.status_screening,
            assigned_user_id=self.recruiter_user,
            notes='Assigned for screening'
        )
        
        # App2: assigned to interview status (matches current_status)
        ApplicationAssignedUserStatuses.objects.create(
            application_id=self.app2,
            status_id=self.status_interview,
            assigned_user_id=self.recruiter_user,
            notes='Assigned for interview'
        )
        
        # App3: assigned to interview status (does NOT match current_status which is screening)
        ApplicationAssignedUserStatuses.objects.create(
            application_id=self.app3,
            status_id=self.status_interview,
            assigned_user_id=self.recruiter_user,
            notes='Assigned for interview but not yet moved'
        )
        
        # Assign app3 to another_recruiter for screening (matches current_status)
        ApplicationAssignedUserStatuses.objects.create(
            application_id=self.app3,
            status_id=self.status_screening,
            assigned_user_id=self.another_recruiter,
            notes='Assigned to another recruiter'
        )
    
    def test_get_user_applications_success(self):
        """Test getting applications assigned to a user where current_status matches"""
        self.client.force_authenticate(user=self.admin_user)
        url = f'/api/users/{self.recruiter_user.id}/applications/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only app1 and app2 should be returned
        
        # Verify the returned applications
        returned_ids = [app['id'] for app in response.data]
        self.assertIn(str(self.app1.id), returned_ids)
        self.assertIn(str(self.app2.id), returned_ids)
        self.assertNotIn(str(self.app3.id), returned_ids)  # app3 doesn't match
    
    def test_get_user_applications_another_user(self):
        """Test getting applications for another recruiter"""
        self.client.force_authenticate(user=self.admin_user)
        url = f'/api/users/{self.another_recruiter.id}/applications/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only app3 should be returned
        
        returned_ids = [app['id'] for app in response.data]
        self.assertIn(str(self.app3.id), returned_ids)
    
    def test_get_user_applications_no_assignments(self):
        """Test getting applications for a user with no assignments"""
        new_user = User.objects.create_user(
            email='newuser@test.com',
            first_name='New',
            last_name='User',
            password='testpass123',
            role=self.recruiter_role
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = f'/api/users/{new_user.id}/applications/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_get_user_applications_unauthenticated(self):
        """Test unauthenticated user cannot access endpoint"""
        url = f'/api/users/{self.recruiter_user.id}/applications/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, http_status.HTTP_401_UNAUTHORIZED)
    
    def test_get_user_applications_response_structure(self):
        """Test the response structure contains expected fields"""
        self.client.force_authenticate(user=self.admin_user)
        url = f'/api/users/{self.recruiter_user.id}/applications/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        
        # Check first application has expected fields
        app = response.data[0]
        expected_fields = [
            'id', 'applicant_name', 'email', 'phone_no', 'job_id', 
            'job_title', 'current_status', 'current_status_name', 
            'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, app)
    
    def test_user_can_access_own_applications(self):
        """Test user can access their own assigned applications"""
        self.client.force_authenticate(user=self.recruiter_user)
        url = f'/api/users/{self.recruiter_user.id}/applications/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_user_cannot_access_other_user_applications(self):
        """Test user cannot access another user's assigned applications"""
        self.client.force_authenticate(user=self.recruiter_user)
        url = f'/api/users/{self.another_recruiter.id}/applications/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, http_status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_access_any_user_applications(self):
        """Test admin can access any user's assigned applications"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Access recruiter_user's applications
        url = f'/api/users/{self.recruiter_user.id}/applications/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        
        # Access another_recruiter's applications
        url = f'/api/users/{self.another_recruiter.id}/applications/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
