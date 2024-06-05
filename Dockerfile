FROM python:3.11

COPY . /app
WORKDIR /app
RUN pip install .[optional]

WORKDIR /downloads

ENTRYPOINT [ "mangadex-downloader" ]

CMD [ "--help" ]