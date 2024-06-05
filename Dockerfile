FROM python:3.11

COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN apt update && apt install wget
RUN wget https://sh.rustup.rs -O rustup.sh
RUN chmod +x ./rustup.sh
RUN ./rustup.sh -q -y
RUN pip install .[optional]

WORKDIR /downloads

ENTRYPOINT [ "mangadex-downloader" ]

CMD [ "--help" ]