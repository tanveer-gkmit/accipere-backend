from django.test import TestCase
from django.contrib.auth import get_user_model
from roles.models import Role

User = get_user_model()


class UserManagerTestCase(TestCase):
    """Test cases for UserManager"""
    
    def setUp(self):
        """Set up test data"""
        self.role = Role.objects.get(name='Recruiter')
        self.admin_role = Role.objects.get(name='Administrator')
    
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