from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.core.cache import cache
from django.db import transaction
from .models import Users, StockData, Transactions
from drf_yasg.utils import swagger_auto_schema
from .serializers import UsersSerializer, StockSerializer, TransactionSerializer
from .task import post_transaction
from datetime import datetime, timedelta

class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

    @swagger_auto_schema(
        operation_description="Retrieve user data. Use Redis to cache user data.",
        responses={200: UsersSerializer()},
    )
    def retrieve(self, request, username, *args, **kwargs):
        user_data = cache.get(f"user_{username}")
        if user_data is None:
            user = Users.objects.get(username=username)
            user_data = {
                'id': user.id,
                'username': user.username,
                'balance': user.balance,
                'created_at': user.created_at
            }
            cache.set(f"user_{username}", user_data)

        return Response(user_data)

    def create(self, request, *args, **kwargs):
        user_serializer_data = UsersSerializer(data=request.data)
        if user_serializer_data.is_valid():
            user_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "User Added Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details", "status": status_code})

class StocksViewSet(viewsets.ModelViewSet):
    queryset = StockData.objects.all()
    serializer_class = StockSerializer

    @swagger_auto_schema(
        operation_description="Retrieve all stock data. Use Redis to cache stock data.",
        responses={200: StockSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        stock_data = cache.get("all_stocks")
        if stock_data is None:
            stocks = self.get_queryset()
            stock_data = list(stocks.values())
            cache.set("all_stocks", stock_data)

        return Response(stock_data)

    def create(self, request, *args, **kwargs):
        stock_serializer_data = StockSerializer(data=request.data)
        if stock_serializer_data.is_valid():
            stock_serializer_data.save()
            cache.delete("all_stocks")
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Stock Added Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details", "status": status_code})

class TransactionsViewSet(viewsets.ModelViewSet):
    queryset = Transactions.objects.all()
    serializer_class = TransactionSerializer

    @swagger_auto_schema(
        operation_description="Create a new transaction. Enqueue Celery task for processing.",
        responses={201: TransactionSerializer()},
    )
    def create(self, request, *args, **kwargs):
        transactions_serializer_data = TransactionSerializer(data=request.data)
        if transactions_serializer_data.is_valid():
            transactions_serializer_data.save()
            post_transaction.delay(
                user_id=request.data['user'],
                ticker=request.data['ticker'],
                transaction_type=request.data['transaction_type'],
                transaction_volume=request.data['transaction_volume']
            )
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Transaction Added Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details", "status": status_code})

    @swagger_auto_schema(
        operation_description="Retrieve all transactions of a specific user.",
        responses={200: TransactionSerializer(many=True)},
    )
    def list(self, request, user_id, *args, **kwargs):
        transactions = Transactions.objects.filter(user=user_id)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve transactions of a specific user between two timestamps.",
        responses={200: TransactionSerializer(many=True)},
    )
    def retrieve(self, request, user_id, start_timestamp=None, end_timestamp=None, *args, **kwargs):
        try:
            start_timestamp = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S") if start_timestamp else datetime.min
            end_timestamp = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S") if end_timestamp else datetime.max

            transactions = Transactions.objects.filter(
                user=user_id,
                timestamp__range=(start_timestamp, end_timestamp)
            )

            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response({"message": "Invalid timestamp format"}, status=status.HTTP_400_BAD_REQUEST)
