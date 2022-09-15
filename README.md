Manga Tagger
---

[![mt-hub-img]][mt-hub-lnk] 
[![Python tests](https://github.com/Banh-Canh/Manga-Tagger/actions/workflows/Run_Tests.yml/badge.svg)](https://github.com/Banh-Canh/Manga-Tagger/actions/workflows/Run_Tests.yml)
## Descriptions

This fork doesn't require FMD2. Running MangaTagger.py will make it watch the directory configured in the settings.json.

Intended to be used in a docker container:
https://hub.docker.com/r/banhcanh/manga-tagger

input Files still have to be named like this (they can be in their own `%MANGA%` directory, or not) : `%MANGA% -.- %CHAPTER%.cbz`

## Features:

* Does not require FMD2
* Only scrapes metadata from [Anilist](https://anilist.co/)
* Support for Manga/Manhwa/Manhua
* Download cover image for each chapter
* Slightly increased filename parsing capability
* Docker image available
* Manga specific configuration

More infos:
https://github.com/Inpacchi/Manga-Tagger

[Check the wiki for install and usage instructions](https://github.com/Banh-Canh/Manga-Tagger/wiki)
---

## Aditional info

I recommend using this with my FMD2 docker image: https://hub.docker.com/r/banhcanh/docker-fmd2

**Note**:
- Environnement Variables overwrite the settings.json. In docker, it is only possible to configure with environnement variables.
- Enabling adult result may give wrong manga match. Make sure the input manga title is as accurate as possible if enabling this or it may confuse Anilist's search.

## License
[MIT](https://choosealicense.com/licenses/mit/)


[mt-hub-img]: https://img.shields.io/docker/pulls/banhcanh/manga-tagger.svg
[mt-hub-lnk]: https://hub.docker.com/r/banhcanh/manga-tagger
