from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

from .models import Transaction
from .serializers import TransactionSerializer


# -------------------------
# REGISTER USER (PUBLIC)
# -------------------------
@api_view(['POST'])
def register_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    # validation
    if not username or not password:
        return Response(
            {"error": "Username and password required"},
            status=400
        )

    # check duplicate user
    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=400
        )

    # create user
    user = User.objects.create_user(username=username, password=password)

    return Response({
        "message": "User created successfully",
        "username": user.username
    })


# -------------------------
# TRANSACTIONS LIST + CREATE
# -------------------------
class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# -------------------------
# TRANSACTION DETAIL (UPDATE / DELETE)
# -------------------------
class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)