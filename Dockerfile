FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Correction du nom du fichier requirements
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Copier tout le code API
COPY api ./api

# Créer le dossier db (sera monté via volume)
RUN mkdir -p /app/db

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
