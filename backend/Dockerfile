FROM python:3.13-slim


WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY wait_for_db.py .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]