FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN pip3 install --upgrade pip
RUN pip3 install sklearn

WORKDIR /app
COPY . /app
RUN pip3 --no-cache-dir install -r requirements.txt
EXPOSE 8000

ENTRYPOINT ["python3"]
CMD ["app.py"]
