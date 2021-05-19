[![mt-hub-img]][mt-hub-lnk] 
## Descriptions

This fork doesn't require FMD2. Running MangaTagger.py will make it watch the directory configured in the settings.json.

Intended to be used in a docker container:
https://hub.docker.com/r/banhcanh/manga-tagger

input Files still have to be named like this (they can be in their own %MANGA% directory, or not) : %MANGA% -.- %CHAPTER%.cbz

## Features:

* Does not require FMD2
* Only scrapes metadata from [Anilist](https://anilist.co/)
* Support for Manga/Manhwa/Manhua
* Download cover image for each chapter
* Slightly increased filename parsing capability
* Docker image available

More infos:
https://github.com/Inpacchi/Manga-Tagger

## Downloading and Running Manga-Tagger
Requirements:
- git
- python
- pip

Clone the sources:
```
git clone https://github.com/Banh-Canh/Manga-Tagger.git
cd Manga-Tagger
```
Configure Manga-Tagger by editing the settings.json, then install the dependencies:
```
pip install -r requirements.txt
```
Finally, run MangaTagger.py:
```
python MangaTagger.py
```

## Running Manga-Tagger with Docker
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

      - MANGA_TAGGER_IMAGE_COVER=true
      - MANGA_TAGGER_ADULT_RESULT=false

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

#    ports:  # Optional, only useful for TCP and Json TCP logging
#      - 1798:1798
#      - 1799:1799

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

I recommend using this with my FMD2 docker image: https://hub.docker.com/r/banhcanh/docker-fmd2

Environnement Variables overwrite the settings.json. In docker, it is only possible to configure with environnement variables.

Enabling adult result may give wrong manga match. Make sure the input manga title is as accurate as possible if enabling this or it may confuse Anilist's search.

Create a file named "exceptions.json" in your configured "data" folder to force MT to fetch metadata of a specific manga.

This will make MT look for metadata from Anilist by searching for this title "Shi ni Modori, Subete wo Sukuu Tame ni Saikyou He to Itaru @comic" for any file that are named in a way where MT would recognize "Shi ni Modori, Subete wo Sukuu Tame ni Saikyou He to Itaru" as the title

```json
{
  "Shi ni Modori, Subete wo Sukuu Tame ni Saikyou He to Itaru":"Shi ni Modori, Subete wo Sukuu Tame ni Saikyou He to Itaru @comic"
}
```

In this case, this title isn't accurate enough and this is we want MT to use "Shi ni Modori, Subete wo Sukuu Tame ni Saikyou He to Itaru @comic" instead.

## License
[MIT](https://choosealicense.com/licenses/mit/)


[mt-hub-img]: https://img.shields.io/docker/pulls/banhcanh/manga-tagger.svg
[mt-hub-lnk]: https://hub.docker.com/r/banhcanh/manga-tagger
