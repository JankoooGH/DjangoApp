# Obraz bazowy
FROM python:3.12-slim

# Nie buforuj .pyc i logów
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Katalog roboczy w kontenerze
WORKDIR /app

# Zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj cały projekt
COPY . .

# Port Django
EXPOSE 8000

# Migracje + uruchomienie serwera
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
