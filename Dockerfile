# Single image shared by the gateway and all mock services; docker-compose.yml
# selects which app to run via CMD override, so no app code changes are needed.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gateway/ gateway/
COPY services/ services/

EXPOSE 8000

CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
