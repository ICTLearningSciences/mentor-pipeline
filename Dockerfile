FROM python:3.7-slim
RUN apt-get update && \
    apt-get install -y \
        ffmpeg \
        git \
        mediainfo \
    && rm -rf /var/lib/apt/lists/*
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt
COPY mentor_pipeline /app/mentor_pipeline
COPY mentor_pipeline_runner.py /app
ENV DATA_MOUNT=/app/mounts/
WORKDIR /app
ENTRYPOINT ["python", "mentor_pipeline_runner.py"]
