FROM ubuntu:18.04
RUN apt-get update && \
    apt-get install -y \
        ffmpeg \
        mediainfo \
        python3.7 \
        python3-pip && \
    rm -rf /var/lib/apt/lists/*
ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt
COPY mentor_pipeline /app/mentor_pipeline
COPY mentor_pipeline_runner.py /app
ENV DATA_MOUNT=/app/mounts/
WORKDIR /app
ENTRYPOINT ["python3", "mentor_pipeline_runner.py"]
