FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /app
EXPOSE 8000