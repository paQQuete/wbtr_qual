FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
WORKDIR /opt/app/src
RUN apt -y update && apt -y install netcat && apt -y install ffmpeg libavcodec-extra libmagic1
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY entrypoint.sh ./entrypoint.sh
EXPOSE 8000
COPY src ./
RUN chmod 777 /opt/app/src/entrypoint.sh
ENTRYPOINT ["/opt/app/src/entrypoint.sh"]

