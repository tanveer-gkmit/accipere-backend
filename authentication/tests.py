from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from roles.models import Role

User = get_user_model()


class LoginTestCase(APITestCase):
    """Test cases for login endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.role = Role.objects.get(name='Recruiter')
        
        self.active_user = User.objects.create_user(
            email='active@test.com',
            first_name='Active',
            last_name='User',
            password='TestPass123!',
            role=self.role,
            is_active=True
        )
    
    def test_login_with_valid_credentials(self):
        """Test successful login"""
        data = {'email': 'active@test.com', 'password': 'TestPass123!'}
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_with_invalid_credentials(self):
        """Test login fails with wrong password"""
        data = {'email': 'active@test.com', 'password': 'WrongPassword'}
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_with_missing_password(self):
        """Test login fails when required password are missing"""
        data = {'email': 'active@test.com'}
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_missing_email(self):
        """Test login fails when required email are missing"""
        data = {'password': 'WrongPassword'}
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshTestCase(APITestCase):
    """Test cases for token refresh endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.refresh_url = reverse('token_refresh')
        self.role = Role.objects.get(name='Recruiter')
        
        self.user = User.objects.create_user(
            email='test@test.com',
            first_name='Test',
            last_name='User',
            password='TestPass123!',
            role=self.role,
            is_active=True
        )
        
        self.refresh_token = RefreshToken.for_user(self.user)
        self.valid_refresh_token = str(self.refresh_token)
    
    def test_refresh_with_valid_token(self):
        """Test successful token refresh"""
        data = {'refresh': self.valid_refresh_token}
        response = self.client.post(self.refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_refresh_with_invalid_token(self):
        """Test refresh fails with invalid token"""
        data = {'refresh': 'invalid.token.here'}
        response = self.client.post(self.refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_refresh_with_blacklisted_token(self):
        """Test refresh fails with blacklisted token"""
        self.refresh_token.blacklist()
        data = {'refresh': self.valid_refresh_token}
        response = self.client.post(self.refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutTestCase(APITestCase):
    """Test cases for logout endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.logout_url = reverse('token_logout')
        self.role = Role.objects.get(name='Recruiter')
        
        self.user = User.objects.create_user(
            email='test@test.com',
            first_name='Test',
            last_name='User',
            password='TestPass123!',
            role=self.role,
            is_active=True
        )
        
        self.refresh_token = RefreshToken.for_user(self.user)
        self.valid_refresh_token = str(self.refresh_token)
        self.access_token = str(self.refresh_token.access_token)
    
    def test_logout_with_valid_token(self):
        """Test successful logout"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {'refresh': self.valid_refresh_token}
        response = self.client.post(self.logout_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data['detail'], 'Successfully logged out.')
    
    def test_logout_without_authentication(self):
        """Test logout fails without authentication"""
        data = {'refresh': self.valid_refresh_token}
        response = self.client.post(self.logout_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_with_invalid_refresh_token(self):
        """Test logout fails with invalid refresh token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {'refresh': 'invalid.token.here'}
        response = self.client.post(self.logout_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
