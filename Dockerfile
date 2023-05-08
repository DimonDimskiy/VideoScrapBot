FROM python:3.10
WORKDIR /scrap_bot
COPY requirements.txt /scrap_bot
RUN apt-get -y update && apt-get install -y ffmpeg\
    && pip install -r requirements.txt
COPY . /scrap_bot
CMD python /scrap_bot/main.py