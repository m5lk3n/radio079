import os

# Populated at build time from the Makefile's VERSION via Docker
# build args (see Dockerfile). Falls back to sensible defaults for local runs.
VERSION = os.environ.get("RADIO079_VERSION", "dev")
