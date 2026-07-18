FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY project.zip /app/

RUN unzip project.zip && rm project.zip

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')\" && gunicorn project.wsgi:application --bind 0.0.0.0:7860 --workers 2"]