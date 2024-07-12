# pull official base image
FROM python:3.8.10-alpine3.13

RUN apk add --no-cache g++ gcc openssl-dev python3-dev && \
    apk add --no-cache postgresql-dev libxml2-dev libxslt-dev libressl-dev && \
    apk add --no-cache musl-dev libffi-dev && \
    apk add --no-cache gettext tzdata && \
    # Pillow Dependencies \
    apk add --no-cache libwebp libwebp-dev && \
    apk add --no-cache freetype-dev fribidi-dev harfbuzz-dev jpeg-dev lcms2-dev openjpeg-dev tcl-dev tiff-dev tk-dev zlib-dev libmagic && \
    pip install --upgrade pip && \
    mkdir /app/

WORKDIR /app

COPY ./requirements /requirements

RUN pip install -r /requirements/base.txt

COPY . /app/

CMD ['echo', 'base image']
