# Use official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies to compile psycopg2-binary
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the entire project code
COPY . .

# Ensure migrations and collectstatic are done before starting Gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn the_samaj_project.wsgi:application --bind 0.0.0.0:8000"]
