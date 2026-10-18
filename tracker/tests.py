from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Transaction, PasswordResetOTP, LoginOTP


class AuthAndTransactionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.username = "testuser"
        self.email = "testuser@example.com"
        self.password = "Password123!"
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    def test_user_registration_with_welcome_email(self):
        response = self.client.post('/api/register/', {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecretPassword1!",
            "confirm_password": "SecretPassword1!"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username="newuser", email="newuser@example.com").exists())

    def test_login_with_2fa_otp_flow(self):
        # Step 1: Submit username and password
        login_res = self.client.post('/api/login/', {
            "username": self.username,
            "password": self.password
        }, format='json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.assertTrue(login_res.data.get("otp_required"))

        # Verify LoginOTP record created
        otp_rec = LoginOTP.objects.filter(user=self.user, is_used=False).first()
        self.assertIsNotNone(otp_rec)
        otp_code = otp_rec.otp

        # Step 2: Verify login OTP
        verify_res = self.client.post('/api/login/verify-otp/', {
            "username": self.username,
            "otp": otp_code
        }, format='json')
        self.assertEqual(verify_res.status_code, status.HTTP_200_OK)
        self.assertIn("access", verify_res.data)
        self.assertEqual(verify_res.data.get("username"), self.username)

    def test_otp_forgot_password_flow(self):
        # 1. Request OTP
        req_res = self.client.post('/api/forgot-password/request-otp/', {
            "email": self.email
        }, format='json')
        self.assertEqual(req_res.status_code, status.HTTP_200_OK)

        otp_record = PasswordResetOTP.objects.filter(user=self.user, is_used=False).first()
        self.assertIsNotNone(otp_record)
        otp_code = otp_record.otp

        # 2. Verify OTP
        verify_res = self.client.post('/api/forgot-password/verify-otp/', {
            "email": self.email,
            "otp": otp_code
        }, format='json')
        self.assertEqual(verify_res.status_code, status.HTTP_200_OK)

        # 3. Reset password
        reset_res = self.client.post('/api/forgot-password/reset/', {
            "email": self.email,
            "otp": otp_code,
            "new_password": "NewSecretPassword123!",
            "confirm_password": "NewSecretPassword123!"
        }, format='json')
        self.assertEqual(reset_res.status_code, status.HTTP_200_OK)

    def test_send_report_email(self):
        login_res = self.client.post('/api/login/', {
            "username": self.username,
            "password": self.password
        }, format='json')
        otp = LoginOTP.objects.filter(user=self.user, is_used=False).first().otp
        token_res = self.client.post('/api/login/verify-otp/', {
            "username": self.username,
            "otp": otp
        }, format='json')
        token = token_res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Send report email
        res = self.client.post('/api/reports/send-email/', {
            "periodLabel": "Monthly (October 2026)",
            "summary": {
                "income": 50000,
                "expense": 15000,
                "balance": 35000,
                "budget": 20000
            }
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_transaction_crud_with_custom_date(self):
        login_res = self.client.post('/api/login/', {
            "username": self.username,
            "password": self.password
        }, format='json')
        otp = LoginOTP.objects.filter(user=self.user, is_used=False).first().otp
        token_res = self.client.post('/api/login/verify-otp/', {
            "username": self.username,
            "otp": otp
        }, format='json')
        token = token_res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Create income with custom date
        custom_date = "2026-05-15T14:30:00Z"
        create_res = self.client.post('/api/transactions/', {
            "title": "Old Project",
            "amount": 25000.0,
            "type": "income",
            "date": custom_date
        }, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        trans_id = create_res.data["id"]

        # List
        list_res = self.client.get('/api/transactions/')
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 1)

        # Delete
        delete_res = self.client.delete(f'/api/transactions/{trans_id}/')
        self.assertEqual(delete_res.status_code, status.HTTP_204_NO_CONTENT)
