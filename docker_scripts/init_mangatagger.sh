#!/bin/bash
chown abc:abc /manga -R
if [ ! -f '/config/settings.json' ]; then mv /settings_docker.json /config/settings.json; fi
ln -s /config/settings.json /app/Manga-Tagger/settings.json
chown abc:abc /config -R
chown abc:abc /app/Manga-Tagger -R
pkill -f MangaTagger.py
sleep 10
cd /app/Manga-Tagger && sudo -u abc python3 MangaTagger.py &
