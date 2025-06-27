FROM python:latest
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y ffmpeg
COPY requirements.txt . /
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /main
COPY /main /main
ENTRYPOINT  ["python","main.py"]