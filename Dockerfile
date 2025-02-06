FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências, incluindo postgresql-client para pg_isready
RUN apk update && apk add --no-cache gcc musl-dev linux-headers postgresql-dev postgresql-client

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY backend /app/backend

CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]
