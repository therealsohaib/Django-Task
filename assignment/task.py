from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from .models import Users, StockData, Transactions
from .serializers import TransactionSerializer

logger = get_task_logger(__name__)

@shared_task
def register_user(username, initial_balance):
    try:
        user = Users.objects.create(username=username, balance=initial_balance)
        logger.info(f"User {username} registered successfully with initial balance {initial_balance}.")
    except Exception as e:
        logger.error(f"Error registering user {username}: {str(e)}")

@shared_task
def retrieve_user_data(username):
    try:
        user = Users.objects.get(username=username)

        cache.set(f"user_{username}", {
            'id': user.id,
            'username': user.username,
            'balance': user.balance,
            'created_at': user.created_at
        })

        logger.info(f"User data retrieved and cached for {username}.")
    except Users.DoesNotExist:
        logger.error(f"User with username {username} does not exist.")

@shared_task
def ingest_stock(ticker, price):
    try:
        stock, created = StockData.objects.get_or_create(ticker=ticker, defaults={'price': price})
        if not created:
            stock.price = price
            stock.save()

        cache.set(ticker, {'ticker': stock.ticker, 'price': stock.price})

        logger.info(f"Stock {ticker} ingested successfully.")
    except Exception as e:
        logger.error(f"Error ingesting stock {ticker}: {str(e)}")

@shared_task
def retrieve_all_stocks():
    try:
        stocks = StockData.objects.all()

        for stock in stocks:
            cache.set(stock.ticker, {'ticker': stock.ticker, 'price': stock.price})

        logger.info("All stock data retrieved and cached.")
    except Exception as e:
        logger.error(f"Error retrieving and caching all stock data: {str(e)}")

@shared_task
def retrieve_specific_stock(ticker):
    try:
        stock = StockData.objects.get(ticker=ticker)

        cache.set(ticker, {'ticker': stock.ticker, 'price': stock.price})

        logger.info(f"Stock {ticker} data retrieved and cached.")
    except StockData.DoesNotExist:
        logger.error(f"Stock with ticker {ticker} does not exist.")

@shared_task
def post_transaction(user_id, ticker, transaction_type, transaction_volume):
    try:
        user = Users.objects.get(id=user_id)

        stock_data = cache.get(ticker)
        if stock_data is None:
            try:
                stock = StockData.objects.get(ticker=ticker)
                stock_data = {'ticker': stock.ticker, 'price': stock.price}
                cache.set(ticker, stock_data)
            except StockData.DoesNotExist:
                logger.warning(f"Stock with ticker {ticker} not found.")
                return

        transaction_price = stock_data['price'] * transaction_volume

        with transaction.atomic():
            if transaction_type == 'buy':
                if user.balance >= transaction_price:
                    user.balance -= transaction_price
                    user.save()
                else:
                    logger.warning(f"Insufficient balance for user {user_id} to buy {transaction_volume} shares of {ticker}.")
                    return
            elif transaction_type == 'sell':
                user.balance += transaction_price
                user.save()

            transaction_data = {
                'user': user,
                'ticker': ticker,
                'transaction_type': transaction_type,
                'transaction_volume': transaction_volume,
                'transaction_price': transaction_price,
                'timestamp': timezone.now(),
            }
            serializer = TransactionSerializer(data=transaction_data)
            if serializer.is_valid():
                serializer.save()

        logger.info(f"Transaction for user {user_id} processed successfully.")
    except Users.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist.")
    except StockData.DoesNotExist:
        logger.error(f"Stock with ticker {ticker} does not exist.")

@shared_task
def retrieve_user_transactions(user_id, start_timestamp, end_timestamp):
    try:
        user = Users.objects.get(id=user_id)
        transactions = Transactions.objects.filter(user=user, timestamp__range=(start_timestamp, end_timestamp))

        logger.info(f"Transactions for user {user_id} retrieved successfully between {start_timestamp} and {end_timestamp}.")

        return transactions
    except Users.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist.")
    except Exception as e:
        logger.error(f"Error retrieving transactions: {str(e)}")
