FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi "uvicorn[standard]" openai python-multipart

COPY app/ ./app/

EXPOSE 6662

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6662"]
