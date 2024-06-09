FROM python:3.11

COPY . /app
WORKDIR /app

# Install mangadex-downloader
RUN pip install --upgrade pip
RUN pip install .

WORKDIR /downloads

ENTRYPOINT [ "mangadex-downloader" ]

CMD [ "--help" ]