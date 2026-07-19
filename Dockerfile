# Runs ShopLite on its own, e.g. as a shared QA environment for manual or Postman testing.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 SHOPLITE_DB=/app/instance/shoplite.sqlite

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0

COPY shoplite ./shoplite
COPY wsgi.py .
RUN useradd --create-home shoplite && mkdir -p instance && chown shoplite instance
USER shoplite

EXPOSE 5000
CMD ["sh", "-c", "flask --app wsgi seed && gunicorn -b 0.0.0.0:5000 -w 2 wsgi:app"]
