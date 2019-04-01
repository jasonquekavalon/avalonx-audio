FROM python:3.7.3-stretch

RUN mkdir /app
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app
EXPOSE 80

ENTRYPOINT ["gunicorn", "-b=0.0.0.0:80", "--worker-class=eventlet", "app:app"]
