FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi "uvicorn[standard]" openai

COPY app/ ./app/

EXPOSE 6661

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6661"]
