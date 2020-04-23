FROM django:latest
FROM python:3.6-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]
