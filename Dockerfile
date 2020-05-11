FROM alpine:latest

RUN apk add --no-cache python3-dev && pip3 install --upgrade pip
RUN pip3 install nltk
RUN python3 -c 'import nltk; nltk.download("words")'
RUN pip3 install sklearn

WORKDIR /app
COPY . /app
RUN pip3 --no-cache-dir install -r requirements.txt
EXPOSE 8000

ENTRYPOINT ["python3"]
CMD ["app.py"]