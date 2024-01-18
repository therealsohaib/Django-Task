# Django Assignment

This project is a Django application that implements an API for managing users, stocks, and transactions. The project utilizes Celery for handling asynchronous tasks and integrates with Redis for caching.

## Requirements 
Make sure you have the following software installed on your machine: - [Docker](https://www.docker.com/)
[PostgreSQL](https://www.postgresql.org/download/)

## Installation 
To set up the project locally, follow these steps: 1. Clone the repository: ```bash git clone https://github.com/therealsohaib/Django-Task.git

## You need to install Celery and Redis in your virtual environments
`pip install celery`
and
`pip install redis`
## Redis is a broker server
Also you need to install Redis in your machine More details about redis  [Redis](https://redis.io/)
## Insert bellow settings in your settings.py
`CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE`
## Run your broker server
`redis-server`
## Next run your Django server
`python manage.py runserver`
## Next step run your Celery worker
`celery -A project_name worker -l info`
example:
`celery -A celearyapp worker -l info`

you will get task list in your console

## next run your scheduler
`celery -A project_name beat -l info`
Example:
`celery -A celeryapp beat -l info`

## API Endpoints

### Users

-   **GET `/api/users/{username}/`**: Retrieve user data.
-   **POST `/api/users/`**: Create a new user.

### Stocks

-   **GET `/api/stocks/`**: Retrieve all stock data.
-   **POST `/api/stocks/`**: Create a new stock.

### Transactions

-   **GET `/api/transactions/{user_id}/`**: Retrieve all transactions of a specific user.
-   **GET `/api/transactions/{user_id}/{start_timestamp}/{end_timestamp}/`**: Retrieve transactions of a specific user between two timestamps.
-   **POST `/api/transactions/`**: Create a new transaction.

For more detailed API documentation, Swagger UI is available at http://localhost:8000/swagger-apis/.
## Unit Tests
Run the unit tests using the following command:
`python manage.py tests`
## Docker

The project can be containerized using Docker. The `docker-compose.yml` file is provided to set up the necessary services.

1.  **Build the Docker images:**
    `docker-compose build` 
    
2.  **Run the Docker containers:**
    `docker-compose up`
## Additional Information

-   The project uses Swagger UI for API documentation. Access it at http://localhost:8000/swagger-apis/.
-   Celery is employed for handling asynchronous tasks.
-   Redis is used for caching user and stock data.

## Resources 
- [Django](https://docs.djangoproject.com/en/5.0/)
- [Redis](https://redis.io/docs/)
- [Celery](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)
- [Swagger UI](https://django-rest-swagger.readthedocs.io/en/latest/)
- [Docker](https://docs.docker.com/get-started/08_using_compose/)
