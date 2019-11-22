PWD=$(shell pwd)
DOCKER_IMAGE?=mentor-pipeline
DOCKER_IMAGE_ID=$(shell docker images -q $(DOCKER_IMAGE))
DOCKER_CONTAINER=mentor-pipeline
PROJECT_ROOT?=$(shell git rev-parse --show-toplevel 2> /dev/null)
WATSON_CREDENTIALS=secrets/watson_credentials.txt
WATSON_USERNAME?=$(shell if [ -f $(WATSON_CREDENTIALS) ]; then head -n 1 $(WATSON_CREDENTIALS); else echo ""; fi)
WATSON_PASSWORD?=$(shell if [ -f $(WATSON_CREDENTIALS) ]; then tail -n 1 $(WATSON_CREDENTIALS); else echo ""; fi)


# Builds the data processing pipeline dockerfile
.PHONY docker-build:
docker-build:
	docker build -t $(DOCKER_IMAGE) .

# virtualenv used for pytest
VENV=.venv
$(VENV):
	$(MAKE) venv-create

.PHONY: venv-create
venv-create: virtualenv-installed
	[ -d $(VENV) ] || virtualenv -p python3 $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r ./requirements.test.txt

virtualenv-installed:
	$(PROJECT_ROOT)/bin/virtualenv_ensure_installed.sh

.PHONY: format
format: $(VENV)
	$(VENV)/bin/black mentor_pipeline

PHONY: test
test: $(VENV)
	$(VENV)/bin/py.test -vv $(args)

.PHONY: test-format
test-format: $(VENV)
	$(VENV)/bin/black --check mentor_pipeline

.PHONY: test-lint
test-lint: $(VENV)
	$(VENV)/bin/flake8 .

test-all: test-format test-lint test

.PHONY: docker-image-exists
docker-image-exists:
ifeq ("$(DOCKER_IMAGE_ID)", "")
	$(MAKE) docker-build
endif

$(WATSON_CREDENTIALS):
	@echo "SET_USERNAME_HERE" > $(WATSON_CREDENTIALS)
	@echo "SET_PASSWORD_HERE" >> $(WATSON_CREDENTIALS)
	chmod 600 $(WATSON_CREDENTIALS)

# Removes single mentor's data files from the local file system
.PHONY: data/mentors/%/clean
data/mentors/%/clean:
	@echo "cleaning data/mentors/$*/build..."
	@rm -rf "data/mentors/$*/build"

# Removes single mentor's data files from the local file system
.PHONY: videos/%/clean
videos/%/clean:
	@echo "cleaning videos/$*..."
	@rm -rf "videos/$*"

# Removes all mentor files from the local file system
.PHONY clean:
clean:
	@for m in data/mentors/*/*; do $(MAKE) data/mentors/$${m}/clean; done
	@for m in videos/*/*; do $(MAKE) videos/$${m}/clean; done


# Runs a shell inside the data processing pipeline dockerfile
.PHONY shell:
shell: docker-image-exists $(WATSON_CREDENTIALS)
	docker run \
			-it \
			--rm \
			--name $(DOCKER_CONTAINER) \
			-e WATSON_USERNAME=$(WATSON_USERNAME) \
			-e WATSON_PASSWORD=$(WATSON_PASSWORD) \
			--entrypoint /bin/bash \
			-v $(PWD)/mentor_pipeline:/app/mentor_pipeline \
			-v $(PWD)/data:/app/mounts/data \
			-v $(PWD)/videos:/app/mounts/videos \
		$(DOCKER_IMAGE)


# Complete build of mentor data
# Runs build if necessary
# Generates data files
# TODO: 1) log every significant action (generating audio, transcribing), 2) build classifier for jd, 3) utterance yaml gets error codes, 4) make delete audio files that failed to transcribe
.PHONY: data/mentors/%
data/mentors/%: data/mentors/%/build/recordings docker-image-exists $(WATSON_CREDENTIALS)
	docker run \
			--rm \
			--name $(DOCKER_CONTAINER) \
			-v $(PWD)/mentor_pipeline:/app/mentor_pipeline \
			-v $(PWD)/data:/app/mounts/data \
			-e WATSON_USERNAME=$(WATSON_USERNAME) \
			-e WATSON_PASSWORD=$(WATSON_PASSWORD) \
			$(DOCKER_IMAGE) --mentor $* --data-update --data=/app/mounts/data/mentors

.PHONY: data/mentors/%/data/update
videos/mentors/%: data/mentors/% docker-image-exists 
	docker run \
			--rm \
			--name $(DOCKER_CONTAINER) \
			-v $(PWD)/mentor_pipeline:/app/mentor_pipeline \
			-v $(PWD)/data:/app/mounts/data \
			-v $(PWD)/videos:/app/mounts/videos \
			-e WATSON_USERNAME=$(WATSON_USERNAME) \
			-e WATSON_PASSWORD=$(WATSON_PASSWORD) \
			$(DOCKER_IMAGE) --mentor $* --videos-update --data=/app/mounts/data/mentors

# # Build checkpoint from mentor data
# .PHONY: checkpoint/%
# checkpoint/%: data/mentors/%
# 	cd $(PROJECT_ROOT)/checkpoint && \
# 	CHECKPOINT=dev_latest $(MAKE) checkpoint-clean/mentor/$* checkpoint-train/mentor/$*
# 	@echo ""
# 	@echo "==== MAKE CHECKPOINT SUCCEEDED! ===="
# 	@echo ""
# 	@echo "If you have generated mentor videos, you can test the environment locally with:"
# 	@echo "	cd .. && make local-run-dev"
# 	@echo ""
# 	@echo "Then view your mentor here:"
# 	@echo "	http://localhost:8080/mentorpanel/?mentor=$*"
