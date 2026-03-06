FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Startup script runs all agents + dashboard
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 3000 8001 8002 8003 8004 8005 8007 8080

CMD ["/app/start.sh"]
