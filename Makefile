IMAGE := radio079
SRC   := $(shell pwd)/src
TTS   := $(shell pwd)/tts
DATA  := $(shell pwd)/data

## help: print this help message
.PHONY: help
help:
	@echo 'usage: make <target>'
	@echo
	@echo '  where <target> is one of the following:'
	@echo
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/ /'

## build: build the docker image
.PHONY: build
build:
	DOCKER_BUILDKIT=1 docker build -t $(IMAGE) .

## check: run code quality checks
.PHONY: check
check: build
	docker run --rm --entrypoint ruff $(IMAGE) check src/
	docker run --rm --entrypoint mypy $(IMAGE) --ignore-missing-imports src/

## run: start the application as a container, generating the podcast audio in the data directory
.PHONY: run
run: build
	docker run --rm \
		--env-file .env \
		-v $(TTS):/app/tts:ro \
		-v $(DATA):/app/data \
		$(IMAGE)

## shell: run a shell in the container
.PHONY: shell
shell: build
	docker run --rm -it \
		--env-file .env \
		-v $(TTS):/app/tts:ro \
		-v $(DATA):/app/data \
		--entrypoint bash $(IMAGE)

## play: play the generated podcast audio on the local machine
.PHONY: play
play:
	mpg123 jingles/intro.mp3
	aplay data/$$(date +%Y%m%d)/weather/weather.wav
	aplay data/$$(date +%Y%m%d)/golem/podcast.wav
	aplay data/$$(date +%Y%m%d)/heise/podcast.wav
	aplay data/$$(date +%Y%m%d)/swr3/podcast.wav

## dev: run the application in development mode, mounting the source code for live editing
.PHONY: dev
dev: build
	docker run --rm -it \
		--env-file .env \
		-v $(SRC):/app/src \
		-v $(TTS):/app/tts:ro \
		-v $(DATA):/app/data \
		--entrypoint bash $(IMAGE)
