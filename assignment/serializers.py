from rest_framework import serializers
from .models  import Users,Transactions,StockData

class UsersSerializer(serializers.ModelSerializer):
    class Meta():
        model = Users
        fields = "__all__"

class StockSerializer(serializers.ModelSerializer):
    class Meta():
        model = StockData
        fields = "__all__"

class TransactionSerializer(serializers.ModelSerializer):
    class Meta():
        model = Transactions
        fields = "__all__"