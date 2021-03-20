## Descriptions

This fork doesn't require FMD2. Running MangaTagger.py will make it watch the directory configured in the settings.json.

Intended to be used in a docker container:
https://hub.docker.com/r/banhcanh/manga-tagger

input Files and folders still have to be named like this : %MANGA%/%MANGA% -.- %CHAPTER%.cbz

## Features:
* Does not require FMD2
* Only scrapes metadata from [Anilist](https://anilist.co/)
* Support for Manga/Manhwa/Manhua
* Download cover image for each chapter
* Slightly increased filename parsing capability
* Docker image available

More infos:
https://github.com/Inpacchi/Manga-Tagger

## Docker
```yaml
---
version: "2.1"
services:
  mangatagger:
    image: banhcanh/manga-tagger
    container_name: mangatagger
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
      - UMASK=022 #optional

      - MANGA_TAGGER_DEBUG_MODE=false

      - MANGA_TAGGER_DRY_RUN=false
      - MANGA_TAGGER_DB_INSERT=false
      - MANGA_TAGGER_RENAME_FILE=false
      - MANGA_TAGGER_WRITE_COMICINFO=false

      - MANGA_TAGGER_THREADS=8
      - MANGA_TAGGER_MAX_QUEUE_SIZE=0

      - MANGA_TAGGER_DB_NAME=manga_tagger
      - MANGA_TAGGER_DB_HOST_ADDRESS=mangatagger-db
      - MANGA_TAGGER_DB_PORT=27017
      - MANGA_TAGGER_DB_USERNAME=manga_tagger
      - MANGA_TAGGER_DB_PASSWORD=Manga4LYFE
      - MANGA_TAGGER_DB_AUTH_SOURCE=admin
      - MANGA_TAGGER_DB_SELECTION_TIMEOUT=10000

      - MANGA_TAGGER_LOGGING_LEVEL=info
      - MANGA_TAGGER_LOGGING_CONSOLE=true
      - MANGA_TAGGER_LOGGING_FILE=true
      - MANGA_TAGGER_LOGGING_JSON=false
      - MANGA_TAGGER_LOGGING_TCP=false
      - MANGA_TAGGER_LOGGING_JSONTCP=false

    volumes:
      - /path/to/config:/config
      - /path/to/library:/manga # directory manga-tagger move tagged files to
      - /path/to/downloads:/downloads # directory manga-tagger watch
    restart: unless-stopped
    depends_on:
      - mangatagger-db
  mangatagger-db: # you can use your own mongodb, edit the manga-tagger settings.json accordingly
    image: mongo
    container_name: mangatagger-db
    volumes:
      - /path/to/mangatagger/db:/data/db # db persistence
    environment:
      MONGO_INITDB_ROOT_USERNAME: manga_tagger
      MONGO_INITDB_ROOT_PASSWORD: Manga4LYFE
      MONGO_INITDB_DATABASE: manga_tagger
    restart: unless-stopped
```  

Environnement Variables overwrite the settings.json.

## License
[MIT](https://choosealicense.com/licenses/mit/)
