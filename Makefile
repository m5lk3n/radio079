IMAGE := radio079
SRC   := $(shell pwd)/src
TTS   := $(shell pwd)/tts

.PHONY: build run shell dev

build:
	DOCKER_BUILDKIT=1 docker build -t $(IMAGE) .

run: build
	docker run --rm \
		--env-file .env \
		-v $(TTS):/app/tts:ro \
		$(IMAGE)

shell: build
	docker run --rm -it \
		--env-file .env \
		-v $(TTS):/app/tts:ro \
		--entrypoint bash $(IMAGE)

dev: build
	docker run --rm -it \
		--env-file .env \
		-v $(SRC):/app/src \
		-v $(TTS):/app/tts:ro \
		--entrypoint bash $(IMAGE)
