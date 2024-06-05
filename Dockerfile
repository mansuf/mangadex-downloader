FROM python:3.11

RUN pip install .[optional]

WORKDIR /downloads

ENTRYPOINT [ "mangadex-downloader" ]

CMD [ "--help" ]