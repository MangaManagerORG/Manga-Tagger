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

## License
[MIT](https://choosealicense.com/licenses/mit/)
