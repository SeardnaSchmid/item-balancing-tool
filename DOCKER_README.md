# Item Balancing Tool - Docker-Anleitung

Diese Anleitung zeigt, wie Sie das Item Balancing Tool als Docker-Container ausführen können.

## Voraussetzungen

- Docker muss auf Ihrem System installiert sein
- Optional: Docker Compose für eine einfachere Verwaltung

## Methode 1: Mit Skript (Empfohlen)

Wir haben Skripte vorbereitet, die den Container automatisch für Sie erstellen und starten:

### Unter Linux/Mac:

```bash
chmod +x start-docker.sh
./start-docker.sh
```

### Unter Windows:

Doppelklicken Sie einfach auf die Datei `start-docker.bat` oder führen Sie sie in der Kommandozeile aus.

## Methode 2: Manuell mit Docker Compose

1. Öffnen Sie ein Terminal/Kommandozeile im Projektverzeichnis
2. Führen Sie den folgenden Befehl aus:

```bash
docker-compose up -d
```

3. Der Container wird im Hintergrund gestartet
4. Öffnen Sie einen Browser und gehen Sie zu http://localhost:8501

## Methode 3: Manuell mit Docker

1. Öffnen Sie ein Terminal/Kommandozeile im Projektverzeichnis
2. Bauen Sie das Docker-Image:

```bash
docker build -t item-balancing-tool .
```

3. Starten Sie den Container:

```bash
docker run -d -p 8501:8501 --name item-balancing-tool -v $(pwd)/data.json:/app/data.json item-balancing-tool
```

4. Öffnen Sie einen Browser und gehen Sie zu http://localhost:8501

## Daten-Persistenz

Die `data.json`-Datei ist als Volume gemountet, sodass Ihre Änderungen auch nach einem Neustart des Containers erhalten bleiben.

## Container stoppen

```bash
docker stop item-balancing-tool
```

## Container neu starten

```bash
docker start item-balancing-tool
```

## Container entfernen

```bash
docker rm item-balancing-tool
```

## Fehlerbehebung

- **Port bereits in Verwendung**: Wenn Port 8501 bereits verwendet wird, können Sie einen anderen Port in der `docker-compose.yml` oder im `docker run`-Befehl angeben.
- **Keine Berechtigung für Volumes**: Unter Linux müssen Sie möglicherweise `sudo` verwenden, um die nötigen Berechtigungen zu erhalten.
