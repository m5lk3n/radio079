FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY radio.png .
COPY jingles/ ./jingles/

# Version metadata, supplied by the Makefile (build args -> runtime env vars).
# Placed after COPY so changing the version does not invalidate the dependency cache.
ARG VERSION=dev
ENV RADIO079_VERSION=$VERSION

EXPOSE 8079

ENTRYPOINT ["python", "src/main.py"]
