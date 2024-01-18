FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY --chown=python:python requirements*.txt ./

RUN pip install --upgrade pip 
RUN pip install gunicorn 
ADD ./requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "-c", "task.wsgi:application"]
