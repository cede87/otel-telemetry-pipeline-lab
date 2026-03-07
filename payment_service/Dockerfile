FROM python:3.11-slim

WORKDIR /app

COPY service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY payment_service /app/payment_service

EXPOSE 8000

CMD ["uvicorn", "payment_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
