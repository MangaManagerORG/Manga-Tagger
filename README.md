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

## License
[MIT](https://choosealicense.com/licenses/mit/)
