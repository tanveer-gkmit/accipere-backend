from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

class HealthCheckTests(APITestCase):
    def test_health_endpoint_returns_ok(self):
        url = reverse('health-check')  # Uses the name from urls.py
        response = self.client.get(url)

        # Assertions
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")
        self.assertIn("message", response.data)
