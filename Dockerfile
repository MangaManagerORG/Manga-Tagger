FROM ghcr.io/linuxserver/baseimage-alpine:3.13

LABEL \
  maintainer="TKVictor-Hang@outlook.fr"

### Set default Timezone, overwrite default MangaTagger settings for the container ###
ENV \
  TZ="Europe/Paris" \
  MANGA_TAGGER_DEBUG_MODE=false \
  MANGA_TAGGER_DATA_DIR="/config/data" \
  MANGA_TAGGER_IMAGE_COVER=true \
  MANGA_TAGGER_IMAGE_DIR="/config/cover" \
  MANGA_TAGGER_ADULT_RESULT=false \
  MANGA_TAGGER_DOWNLOAD_DIR="/downloads" \
  MANGA_TAGGER_LIBRARY_DIR="/manga" \
  MANGA_TAGGER_LOGGING_DIR="/config/logs" \
  MANGA_TAGGER_DRY_RUN=false \
  MANGA_TAGGER_DB_INSERT=false \
  MANGA_TAGGER_RENAME_FILE=false \
  MANGA_TAGGER_WRITE_COMICINFO=false \
  MANGA_TAGGER_THREADS=8 \
  MANGA_TAGGER_MAX_QUEUE_SIZE=0 \
  MANGA_TAGGER_DB_NAME=manga_tagger \
  MANGA_TAGGER_DB_HOST_ADDRESS=mangatagger-db \
  MANGA_TAGGER_DB_PORT=27017 \
  MANGA_TAGGER_DB_USERNAME=manga_tagger \
  MANGA_TAGGER_DB_PASSWORD=Manga4LYFE \
  MANGA_TAGGER_DB_AUTH_SOURCE=admin \
  MANGA_TAGGER_DB_SELECTION_TIMEOUT=10000 \
  MANGA_TAGGER_LOGGING_LEVEL=info \
  MANGA_TAGGER_LOGGING_CONSOLE=true \
  MANGA_TAGGER_LOGGING_FILE=true \
  MANGA_TAGGER_LOGGING_JSON=false \
  MANGA_TAGGER_LOGGING_TCP=false \
  MANGA_TAGGER_LOGGING_JSONTCP=false

### Upgrade ###
RUN \
  apk update && apk upgrade

### Manga Tagger ###
COPY . /app/Manga-Tagger

RUN \
  echo "Installing Manga-Tagger"

COPY root/ /

### Dependencies ###
RUN \
  echo "Install dependencies" && \
  echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories && \
  apk add --no-cache --update \
    python3 py3-pip py3-numpy py3-multidict py3-yarl \
    py3-psutil py3-watchdog py3-requests py3-tz \
    build-base jpeg-dev zlib-dev python3-dev && \
  pip3 install --no-cache-dir -r /app/Manga-Tagger/requirements.txt && \
  mkdir /manga && \
  mkdir /downloads

VOLUME /config
