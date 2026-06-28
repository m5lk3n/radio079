# Common base: runtime dependencies + a static ffmpeg binary.
#
# We only use ffmpeg for audio loudness normalisation (the `loudnorm` filter),
# so instead of Debian's `ffmpeg` package -- which drags in the full video-codec,
# Mesa/LLVM and flite-voice tree (~450MB) -- we copy a single self-contained
# static binary. This also means the image needs no apt packages at all.
FROM python:3.12-slim AS base

WORKDIR /app

COPY --from=mwader/static-ffmpeg:7.1 /ffmpeg /usr/local/bin/ffmpeg

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

# Dev image: adds linters / type-checker for `make check`. Built with
# `--target dev`; the default build target is the slim `runtime` stage below.
FROM base AS dev
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Default build target: the runtime image, free of dev tooling.
FROM base AS runtime
