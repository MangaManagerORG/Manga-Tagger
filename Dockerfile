FROM ghcr.io/linuxserver/baseimage-alpine:3.13
ENV TZ="Etc/UTC"

### Upgrade
RUN \
  apk update && apt upgrade

### Manga Tagger ###
COPY . /app/Manga-Tagger

RUN \
  echo "Installing Manga-Tagger" && \
  chown abc:abc /app/Manga-Tagger -R && \
  cp /app/Manga-Tagger/root/* / -r

RUN \
  echo "Install dependencies" && \
  echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories && \
  apk add --no-cache --update python3 py3-pip python3-tkinter py3-numpy py3-multidict py3-yarl \
    py3-psutil py3-watchdog py3-requests py3-tz \
    build-base jpeg-dev zlib-dev \
    python3-dev

RUN \
  pip3 install pymongo python_json_logger image BeautifulSoup4 && \
  mkdir /manga

# Execute commands at runtime, set permissions

VOLUME /config
