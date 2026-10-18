from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db import transaction as db_transaction
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
import hmac
import hashlib
import subprocess
import sys
import os
from pathlib import Path

from .models import Transaction, PasswordResetOTP, LoginOTP
from .serializers import TransactionSerializer


# -------------------------
# REGISTER USER (PUBLIC)
# -------------------------
@api_view(['POST'])
def register_user(request):
    username = request.data.get("username", "").strip()
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password")
    confirm_password = request.data.get("confirm_password")

    # Basic presence validation
    if not username or not password:
        return Response(
            {"error": "Username and password are required."},
            status=400
        )

    if not email:
        return Response(
            {"error": "Email address is required."},
            status=400
        )

    if "@" not in email or "." not in email:
        return Response(
            {"error": "Please enter a valid email address (e.g. name@example.com)."},
            status=400
        )

    if confirm_password is not None and password != confirm_password:
        return Response(
            {"error": "Passwords do not match. Please verify both passwords."},
            status=400
        )

    if len(password) < 4:
        return Response(
            {"error": "Password must be at least 4 characters long."},
            status=400
        )

    # Check duplicate username
    if User.objects.filter(username__iexact=username).exists():
        return Response(
            {"error": "Username already exists. Please pick another one."},
            status=400
        )

    # Check duplicate email
    if User.objects.filter(email__iexact=email).exists():
        return Response(
            {"error": "An account with this email address already exists. Please log in."},
            status=400
        )

    # Create user with email
    user = User.objects.create_user(username=username, email=email, password=password)

    # Send Welcome Email
    welcome_subject = f"Welcome to FinTrack, {user.username}! 🚀"
    welcome_message = (
        f"Hello {user.username},\n\n"
        f"Welcome to FinTrack - your personal wealth & expense management hub!\n\n"
        f"We are thrilled to have you onboard. With FinTrack, you can:\n"
        f"• Track your daily, monthly, and yearly income & expenses\n"
        f"• Set monthly target budgets to stay in control\n"
        f"• Export beautiful reports in Excel (.xlsx) and PDF\n"
        f"• Secure your account with Two-Factor OTP authentication\n\n"
        f"Your registered email address is: {user.email}\n\n"
        f"Best regards,\nFinTrack Team"
    )
    try:
        send_mail(
            subject=welcome_subject,
            message=welcome_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[Email Error] Welcome email failed: {e}")

    return Response({
        "message": "User registered successfully! A welcome email has been sent. You can now log in.",
        "username": user.username,
        "email": user.email,
    })


# -------------------------
# LOGIN USER: STEP 1 (VERIFY CREDENTIALS & SEND LOGIN OTP)
# -------------------------
@api_view(['POST'])
def login_user(request):
    login_id = request.data.get("username", "").strip()
    password = request.data.get("password", "")

    if not login_id or not password:
        return Response(
            {"error": "Username/Email and password are required."},
            status=400
        )

    # Check if user entered email or username
    user_obj = None
    if "@" in login_id:
        user_obj = User.objects.filter(email__iexact=login_id).first()
    if not user_obj:
        user_obj = User.objects.filter(username__iexact=login_id).first()

    if not user_obj:
        return Response(
            {"error": "Account does not exist. Please check your username/email or register."},
            status=400
        )

    # Authenticate credentials
    user = authenticate(username=user_obj.username, password=password)
    if user is None:
        return Response(
            {"error": "Invalid password. Please check your credentials."},
            status=400
        )

    # Generate Login 2FA OTP
    otp_obj = LoginOTP.generate_otp_for_user(user)

    target_email = user.email or login_id
    subject = f"FinTrack: Your Login Verification Code is {otp_obj.otp}"
    message = (
        f"Hello {user.username},\n\n"
        f"Your 6-digit FinTrack Login Verification Code is: {otp_obj.otp}\n\n"
        f"This code will expire in 10 minutes.\n"
        f"Please enter this code on the login screen to access your account.\n\n"
        f"If you did not attempt to log in, please secure your account immediately.\n\n"
        f"FinTrack Security Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[target_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[Email Error] Login OTP failed: {e}")

    # Obfuscate email
    parts = target_email.split("@")
    masked_email = f"{parts[0][:2]}***@{parts[1]}" if len(parts) == 2 else target_email

    resp = {
        "otp_required": True,
        "message": f"Verification code sent to {masked_email}",
        "username": user.username,
        "email": target_email,
    }
    if settings.DEBUG:
        resp["dev_otp"] = otp_obj.otp

    return Response(resp)


# -------------------------
# LOGIN USER: STEP 2 (VERIFY LOGIN OTP & ISSUE TOKENS)
# -------------------------
@api_view(['POST'])
def verify_login_otp(request):
    login_id = request.data.get("username", "") or request.data.get("email", "")
    login_id = str(login_id).strip()
    otp_code = str(request.data.get("otp", "")).strip()

    if not login_id or not otp_code:
        return Response({"error": "Username/Email and OTP code are required."}, status=400)

    user = User.objects.filter(email__iexact=login_id).first() or \
           User.objects.filter(username__iexact=login_id).first()

    if not user:
        return Response({"error": "Account not found."}, status=404)

    otp_obj = LoginOTP.objects.filter(
        user=user, otp=otp_code, is_used=False
    ).order_by('-created_at').first()

    if not otp_obj or not otp_obj.is_valid():
        return Response(
            {"error": "Invalid or expired login code. Please request a new verification code."},
            status=400
        )

    # Mark OTP as used
    otp_obj.is_used = True
    otp_obj.save()

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "username": user.username,
        "email": user.email,
        "message": "Login successful"
    })


# -------------------------
# LOGIN: RESEND LOGIN OTP
# -------------------------
@api_view(['POST'])
def resend_login_otp(request):
    login_id = request.data.get("username", "") or request.data.get("email", "")
    login_id = str(login_id).strip()

    if not login_id:
        return Response({"error": "Username or Email is required."}, status=400)

    user = User.objects.filter(email__iexact=login_id).first() or \
           User.objects.filter(username__iexact=login_id).first()

    if not user:
        return Response({"error": "Account not found."}, status=404)

    otp_obj = LoginOTP.generate_otp_for_user(user)
    target_email = user.email or login_id

    subject = f"FinTrack: Your Login Verification Code is {otp_obj.otp}"
    message = (
        f"Hello {user.username},\n\n"
        f"Your new 6-digit FinTrack Login Verification Code is: {otp_obj.otp}\n\n"
        f"This code will expire in 10 minutes.\n\n"
        f"FinTrack Security Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[target_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[Email Error] Resend Login OTP failed: {e}")

    resp = {
        "message": "A new verification code has been sent to your email.",
        "username": user.username,
        "email": target_email,
    }
    if settings.DEBUG:
        resp["dev_otp"] = otp_obj.otp

    return Response(resp)


# -------------------------
# FORGOT PASSWORD: 1. REQUEST OTP
# -------------------------
@api_view(['POST'])
def request_password_reset_otp(request):
    identifier = request.data.get("email", "") or request.data.get("username", "")
    identifier = str(identifier).strip()

    if not identifier:
        return Response(
            {"error": "Please provide your registered email address or username."},
            status=400
        )

    user = None
    if "@" in identifier:
        user = User.objects.filter(email__iexact=identifier).first()
    if not user:
        user = User.objects.filter(username__iexact=identifier).first()

    if not user:
        return Response(
            {"error": "No account found matching this email or username."},
            status=404
        )

    target_email = user.email or (identifier if "@" in identifier else "")
    if not target_email:
        return Response(
            {"error": "No email address linked with this account. Please contact support."},
            status=400
        )

    # Generate 6-digit OTP
    otp_obj = PasswordResetOTP.generate_otp_for_user(user)

    # Send OTP Email
    subject = f"FinTrack: Your Password Reset Verification Code is {otp_obj.otp}"
    message = (
        f"Hello {user.username},\n\n"
        f"You requested to reset your password on FinTrack.\n\n"
        f"Your 6-digit OTP verification code is: {otp_obj.otp}\n\n"
        f"This code will expire in 10 minutes.\n"
        f"If you did not make this request, you can safely ignore this email.\n\n"
        f"Best regards,\nFinTrack Security Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[target_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[Email Error] Could not send via SMTP: {e}")

    # Obfuscate email for user privacy display
    parts = target_email.split("@")
    masked_email = f"{parts[0][:2]}***@{parts[1]}" if len(parts) == 2 else target_email

    resp = {
        "message": f"Verification code sent to {masked_email}",
        "email": target_email,
        "username": user.username,
    }
    if settings.DEBUG:
        resp["dev_otp"] = otp_obj.otp

    return Response(resp)


# -------------------------
# FORGOT PASSWORD: 2. VERIFY OTP
# -------------------------
@api_view(['POST'])
def verify_password_reset_otp(request):
    identifier = request.data.get("email", "") or request.data.get("username", "")
    identifier = str(identifier).strip()
    otp_code = str(request.data.get("otp", "")).strip()

    if not identifier or not otp_code:
        return Response({"error": "Email/Username and OTP code are required."}, status=400)

    user = User.objects.filter(email__iexact=identifier).first() or \
           User.objects.filter(username__iexact=identifier).first()

    if not user:
        return Response({"error": "Account not found."}, status=404)

    otp_obj = PasswordResetOTP.objects.filter(
        user=user, otp=otp_code, is_used=False
    ).order_by('-created_at').first()

    if not otp_obj or not otp_obj.is_valid():
        return Response(
            {"error": "Invalid or expired OTP code. Please request a new verification code."},
            status=400
        )

    return Response({"message": "OTP verified successfully. You can now set your new password."})


# -------------------------
# FORGOT PASSWORD: 3. RESET PASSWORD WITH OTP
# -------------------------
@api_view(['POST'])
def reset_password_with_otp(request):
    identifier = request.data.get("email", "") or request.data.get("username", "")
    identifier = str(identifier).strip()
    otp_code = str(request.data.get("otp", "")).strip()
    new_password = request.data.get("new_password", "")
    confirm_password = request.data.get("confirm_password", "")

    if not identifier or not new_password:
        return Response(
            {"error": "Email/Username, OTP, and new password are required."},
            status=400
        )

    if confirm_password and new_password != confirm_password:
        return Response({"error": "Passwords do not match."}, status=400)

    if len(new_password) < 4:
        return Response({"error": "Password must be at least 4 characters long."}, status=400)

    user = User.objects.filter(email__iexact=identifier).first() or \
           User.objects.filter(username__iexact=identifier).first()

    if not user:
        return Response({"error": "Account not found."}, status=404)

    if otp_code:
        otp_obj = PasswordResetOTP.objects.filter(
            user=user, otp=otp_code, is_used=False
        ).order_by('-created_at').first()

        if not otp_obj or not otp_obj.is_valid():
            return Response(
                {"error": "Invalid or expired OTP code. Please request a new code."},
                status=400
            )
        otp_obj.is_used = True
        otp_obj.save()

    user.set_password(new_password)
    user.save()

    return Response({
        "message": "Password reset successfully! Please login with your new password."
    })


# -------------------------
# BACKWARD COMPATIBLE / DIRECT FORGOT PASSWORD
# -------------------------
@api_view(['POST'])
def forgot_password(request):
    otp = request.data.get("otp")
    if otp:
        return reset_password_with_otp(request)
    return reset_password_with_otp(request)


# -------------------------
# SEND FINANCIAL REPORT VIA EMAIL (AUTHENTICATED)
# -------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_report_email(request):
    user = request.user
    recipient_email = request.data.get("email", "").strip() or user.email

    if not recipient_email or "@" not in recipient_email:
        return Response(
            {"error": "No valid email address found to send report to. Please enter an email."},
            status=400
        )

    period_label = request.data.get("periodLabel", "All Time")
    summary = request.data.get("summary", {})
    income = float(summary.get("income", 0))
    expense = float(summary.get("expense", 0))
    balance = float(summary.get("balance", 0))
    budget_val = summary.get("budget", 0)

    subject = f"FinTrack Financial Report: {period_label} ({user.username})"
    message = (
        f"Hello {user.username},\n\n"
        f"Here is your FinTrack Financial Report for {period_label}:\n\n"
        f"=================================================\n"
        f"FINTRACK FINANCIAL SUMMARY - {period_label.upper()}\n"
        f"=================================================\n"
        f"Total Income:     INR {income:,.2f}\n"
        f"Total Expenses:   INR {expense:,.2f}\n"
        f"Net Cashflow:     INR {balance:,.2f} ({'Surplus' if balance >= 0 else 'Deficit'})\n"
    )

    if budget_val:
        message += f"Monthly Budget:   INR {float(budget_val):,.2f}\n"

    message += (
        f"=================================================\n\n"
        f"Generated automatically by FinTrack Wealth Hub on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} UTC.\n\n"
        f"Stay on top of your financial goals!\n"
        f"FinTrack App Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        return Response({
            "message": f"Financial report successfully sent to {recipient_email}!"
        })
    except Exception as e:
        return Response({"error": f"Failed to send email: {str(e)}"}, status=500)


# -------------------------
# TRANSACTIONS LIST + CREATE
# -------------------------
class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        raw_date = self.request.data.get("date")
        if raw_date:
            parsed = parse_datetime(str(raw_date))
            if parsed:
                serializer.save(user=self.request.user, date=parsed)
                return
        serializer.save(user=self.request.user)


# -------------------------
# TRANSACTION DETAIL (UPDATE / DELETE)
# -------------------------
class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


# -------------------------
# BACKUP: EXPORT (AUTHENTICATED)
# -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_backup(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    data = TransactionSerializer(transactions, many=True).data
    return Response({
        "version": "1.0",
        "exported_at": timezone.now().isoformat(),
        "username": request.user.username,
        "count": len(data),
        "transactions": data
    })


# -------------------------
# BACKUP: RESTORE (AUTHENTICATED)
# -------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_backup(request):
    payload = request.data
    tx_list = payload.get("transactions")
    if not isinstance(tx_list, list):
        return Response({"error": "Invalid backup format: 'transactions' list required"}, status=400)

    mode = payload.get("mode", "merge")  # "merge" or "replace"

    try:
        with db_transaction.atomic():
            if mode == "replace":
                Transaction.objects.filter(user=request.user).delete()

            created = []
            for item in tx_list:
                title = str(item.get("title", "")).strip()
                try:
                    amount = float(item.get("amount", 0))
                except (ValueError, TypeError):
                    continue

                ttype = str(item.get("type", "expense")).lower()
                if ttype not in ["income", "expense"]:
                    ttype = "expense"

                if not title or amount <= 0:
                    continue

                t = Transaction(user=request.user, title=title, amount=amount, type=ttype)
                raw_date = item.get("date")
                if raw_date:
                    parsed = parse_datetime(str(raw_date))
                    if parsed:
                        t.date = parsed
                created.append(t)

            Transaction.objects.bulk_create(created)

        return Response({
            "message": f"Successfully restored {len(created)} transactions",
            "restored_count": len(created)
        })
    except Exception as e:
        return Response({"error": f"Failed to restore backup: {str(e)}"}, status=400)


# -------------------------
# CI/CD: GITHUB AUTO-DEPLOY WEBHOOK
# -------------------------
@csrf_exempt
@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def github_deploy_webhook(request):
    """
    CI/CD Webhook for GitHub -> PythonAnywhere auto-deployment.
    Triggered automatically when code is pushed to GitHub repository.
    Verifies GitHub HMAC-SHA256 signature (or X-Deploy-Token / ?token=).
    Executes:
      1. git pull
      2. python manage.py migrate
      3. Touches PythonAnywhere WSGI file to trigger instant application reload.
    """
    secret = os.getenv('DEPLOY_SECRET', '').strip()
    if not secret:
        return Response({
            "error": "DEPLOY_SECRET is not configured in server environment (.env)."
        }, status=500)

    # 1. Verification
    authenticated = False

    # Check standard GitHub X-Hub-Signature-256
    sig_header = request.headers.get('X-Hub-Signature-256', '')
    if sig_header.startswith('sha256='):
        expected_sig = 'sha256=' + hmac.new(
            secret.encode('utf-8'),
            request.body,
            hashlib.sha256
        ).hexdigest()
        if hmac.compare_digest(sig_header, expected_sig):
            authenticated = True

    # Fallback to header or query parameter (allows easy manual test)
    token = request.headers.get('X-Deploy-Token') or request.GET.get('token')
    if token and hmac.compare_digest(token, secret):
        authenticated = True

    if not authenticated:
        return Response({
            "error": "Unauthorized: Invalid or missing webhook signature/token."
        }, status=403)

    # Acknowledge GitHub ping event
    if request.headers.get('X-GitHub-Event') == 'ping':
        return Response({
            "status": "pong",
            "message": "Webhook connection verified successfully."
        })

    base_dir = settings.BASE_DIR
    results = {}

    # 2. git pull
    try:
        git_proc = subprocess.run(
            ['git', 'pull'],
            cwd=base_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        results['git_pull'] = {
            "stdout": git_proc.stdout.strip(),
            "stderr": git_proc.stderr.strip(),
            "returncode": git_proc.returncode
        }
    except Exception as e:
        results['git_pull'] = {"error": str(e)}

    # 3. python manage.py migrate
    try:
        migrate_proc = subprocess.run(
            [sys.executable, str(base_dir / 'manage.py'), 'migrate'],
            cwd=base_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        results['migrate'] = {
            "stdout": migrate_proc.stdout.strip(),
            "stderr": migrate_proc.stderr.strip(),
            "returncode": migrate_proc.returncode
        }
    except Exception as e:
        results['migrate'] = {"error": str(e)}

    # 4. Touch PythonAnywhere WSGI file to trigger reload
    reloaded = False
    target_wsgi = os.getenv('PYTHONANYWHERE_WSGI_FILE', '/var/www/apsarar_pythonanywhere_com_wsgi.py')

    if os.path.exists(target_wsgi):
        try:
            os.utime(target_wsgi, None)
            reloaded = True
        except Exception:
            pass

    if not reloaded:
        var_www = Path('/var/www')
        if var_www.exists():
            for wsgi_file in var_www.glob('*_wsgi.py'):
                try:
                    os.utime(str(wsgi_file), None)
                    reloaded = True
                except Exception:
                    pass

    results['reloaded'] = reloaded

    return Response({
        "status": "success",
        "message": "Deployment completed successfully.",
        "details": results
    })