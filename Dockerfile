FROM python:3.13-alpine

COPY . /app
WORKDIR /app

# Setup dependencies
RUN apk add --no-cache jpeg-dev zlib-dev build-base python3-dev freetype-dev

# Install mangadex-downloader
RUN pip install --upgrade pip
RUN pip install .

WORKDIR /downloads

ENTRYPOINT [ "mangadex-downloader" ]

CMD [ "--help" ]