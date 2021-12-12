FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive

MAINTAINER fnndsc "hello@barikoi.com"
RUN apt-get update \
    && apt-get install -y python3-pip python3-dev \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 install --upgrade pip
RUN apt-get install -y libenchant1c2a
RUN apt-get install -q sqlite3
RUN apt-get install libsqlite3-mod-spatialite

WORKDIR /app
COPY . /app
RUN pip3 --no-cache-dir install -r requirements.txt
EXPOSE 8000

ENTRYPOINT ["python3"]
CMD ["app.py"]
