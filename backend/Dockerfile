FROM python:3.11
# Instala o cliente sqlite3 para fins de depuração
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
EXPOSE 8888
CMD ["python", "-m", "app.server"]
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

