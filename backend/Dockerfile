FROM python:3.11

RUN apt-get update && apt-get install -y default-mysql-client && rm -rf /var/lib/apt/lists/*

# Ustawienie katalogu roboczego w kontenerze
WORKDIR /app

# Skopiowanie plików aplikacji do kontenera
COPY . /app

# Instalacja zależności (jeśli masz plik requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Określenie portu, na którym działa aplikacja
EXPOSE 5000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]