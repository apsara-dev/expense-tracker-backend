from django.urls import path
from .views import (
    register_user,
    login_user,
    verify_login_otp,
    resend_login_otp,
    forgot_password,
    request_password_reset_otp,
    verify_password_reset_otp,
    reset_password_with_otp,
    send_report_email,
    TransactionListCreateView,
    TransactionDetailView,
    export_backup,
    restore_backup,
    github_deploy_webhook,
)

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', register_user),
    path('register', register_user),
    path('login/', login_user),
    path('login', login_user),
    path('login/verify-otp/', verify_login_otp),
    path('login/verify-otp', verify_login_otp),
    path('login/resend-otp/', resend_login_otp),
    path('login/resend-otp', resend_login_otp),
    path('forgot-password/', forgot_password),
    path('forgot-password', forgot_password),
    path('forgot-password/request-otp/', request_password_reset_otp),
    path('forgot-password/request-otp', request_password_reset_otp),
    path('forgot-password/verify-otp/', verify_password_reset_otp),
    path('forgot-password/verify-otp', verify_password_reset_otp),
    path('forgot-password/reset/', reset_password_with_otp),
    path('forgot-password/reset', reset_password_with_otp),
    path('reports/send-email/', send_report_email),
    path('reports/send-email', send_report_email),
    path('refresh/', TokenRefreshView.as_view()),
    path('refresh', TokenRefreshView.as_view()),

    path('transactions/', TransactionListCreateView.as_view()),
    path('transactions', TransactionListCreateView.as_view()),
    path('transactions/<int:pk>/', TransactionDetailView.as_view()),
    path('transactions/<int:pk>', TransactionDetailView.as_view()),

    path('backup/export/', export_backup),
    path('backup/export', export_backup),
    path('backup/restore/', restore_backup),
    path('backup/restore', restore_backup),
    path('deploy/', github_deploy_webhook),
    path('deploy', github_deploy_webhook),
]