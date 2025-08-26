FROM python:3.9-slim

LABEL maintainer="Item Balancing Tool"
LABEL version="1.0"
LABEL description="Item Balancing Tool für Spiele-Balancing"

WORKDIR /app

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungsdateien kopieren
COPY . .

# Create a writable data directory for persistent storage
RUN mkdir -p /app/data && chmod 755 /app/data

# Ensure the app can write to its own directory
RUN chmod 755 /app

# Port freigeben
EXPOSE 8501

# Health check einrichten
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/ || exit 1

# Streamlit-Konfiguration für Docker
RUN mkdir -p /root/.streamlit
RUN echo "\
[server]\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
" > /root/.streamlit/config.toml

# Anwendung starten
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py", "--server.port=8501", "--server.address=0.0.0.0"]
