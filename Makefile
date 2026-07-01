IMAGE := lttl.dev/radio079
SRC   := $(shell pwd)/src
TTS   := $(shell pwd)/tts
DATA  := $(shell pwd)/data
# grab the latest git tag, remove the 'v' prefix if present, and handle dirty/dev commits
VERSION ?= $(shell git describe --tags --always --dirty | sed 's/^v//')

## help: print this help message
.PHONY: help
help:
	@echo 'usage: make <target>'
	@echo
	@echo '  where <target> is one of the following:'
	@echo
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/ /'


.PHONY: needs_aplay
needs_aplay:
	@command -v aplay >/dev/null 2>&1 || { echo >&2 "error: aplay is required to play the generated audio. Please install alsa-utils."; exit

## build: build the docker image
.PHONY: build
build:
	DOCKER_BUILDKIT=1 docker build \
		--target runtime \
		--build-arg VERSION=$(VERSION) \
		-t $(IMAGE):$(VERSION) .

## check: run code quality checks
.PHONY: check
check:
	DOCKER_BUILDKIT=1 docker build \
		--target dev \
		--build-arg VERSION=$(VERSION) \
		-t $(IMAGE):$(VERSION)-dev .
	docker run --rm --entrypoint ruff $(IMAGE):$(VERSION)-dev check src/
	docker run --rm --entrypoint mypy $(IMAGE):$(VERSION)-dev --ignore-missing-imports src/

## run: start the application as a container, generating the podcast audio in the data directory
.PHONY: run
run: build
	docker run --rm \
		--env-file .env \
		-v $(TTS):/app/tts:ro \
		-v $(DATA):/app/data \
		$(IMAGE):$(VERSION)

## shell: run a shell in the container
.PHONY: shell
shell: build
	docker run --rm -it \
		--env-file .env \
		-v $(TTS):/app/tts:ro \
		-v $(DATA):/app/data \
		--entrypoint bash $(IMAGE):$(VERSION)

## webserver: start the web streaming server on port 8079
.PHONY: webserver
webserver: build
	docker run --rm \
		--env-file .env \
		-v $(TTS):/app/tts:ro \
		-v $(DATA):/app/data \
		-p 127.0.0.1:8079:8079 \
		$(IMAGE):$(VERSION) --webserver

## play: play the generated audio on the local machine, without jingles, using aplay
.PHONY: play
play: needs_aplay
	aplay data/$$(date +%Y%m%d)/weather/weather.wav
	aplay data/$$(date +%Y%m%d)/heise/podcast.wav
	aplay data/$$(date +%Y%m%d)/tagesschau/podcast.wav
	
## clean-images: remove old container images, keeping only the current version, plus dangling layers
.PHONY: clean-images
clean-images:
	docker images $(IMAGE) --format '{{.Repository}}:{{.Tag}}' | \
		grep -F -x -v -e '$(IMAGE):$(VERSION)' -e '$(IMAGE):$(VERSION)-dev' | \
		xargs -r docker rmi
	docker image prune -f

## dev: run the application in development mode, mounting the source code for live editing
.PHONY: dev
dev: build
	docker run --rm -it \
		--env-file .env \
		-v $(SRC):/app/src \
		-v $(TTS):/app/tts:ro \
		-v $(DATA):/app/data \
		--entrypoint bash $(IMAGE):$(VERSION)
