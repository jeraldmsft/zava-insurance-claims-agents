FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Fix line endings and make executable
RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*
RUN dos2unix /app/start.sh && chmod +x /app/start.sh

EXPOSE 3000 8001 8002 8003 8004 8005 8007 8080

CMD ["/app/start.sh"]
