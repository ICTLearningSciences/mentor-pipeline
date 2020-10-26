PWD=$(shell pwd)
DOCKER_IMAGE?=mentor-pipeline
DOCKER_IMAGE_ID=$(shell docker images -q $(DOCKER_IMAGE))
DOCKER_CONTAINER=mentor-pipeline
WATSON_CREDENTIALS=secrets/watson_credentials.txt
WATSON_USERNAME?=$(shell if [ -f $(WATSON_CREDENTIALS) ]; then head -n 1 $(WATSON_CREDENTIALS); else echo ""; fi)
WATSON_PASSWORD?=$(shell if [ -f $(WATSON_CREDENTIALS) ]; then tail -n 1 $(WATSON_CREDENTIALS); else echo ""; fi)


# virtualenv used for pytest
VENV=.venv
$(VENV):
	$(MAKE) $(VENV)-update

.PHONY: $(VENV)-update
$(VENV)-update: virtualenv-installed
	[ -d $(VENV) ] || virtualenv -p python3.8 $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r ./requirements.test.txt

virtualenv-installed:
	./bin/virtualenv_ensure_installed.sh

# Removes all mentor files from the local file system
.PHONY: clean
clean:
	rm -rf .venv htmlcov .coverage 

.PHONY: deps-update
deps-update: $(VENV)
	. $(VENV)/bin/activate && pip-upgrade requirements*

# Builds the data processing pipeline dockerfile
.PHONY docker-build:
docker-build:
	docker build -t $(DOCKER_IMAGE) .

.PHONY: format
format: $(VENV)
	$(VENV)/bin/black mentor_pipeline tests

PHONY: test
test: $(VENV)
	$(VENV)/bin/py.test -vv $(args)

.PHONY: test-all
test-all: test-format test-lint test-types test-license test

.PHONY: test-format
test-format: $(VENV)
	$(VENV)/bin/black --check mentor_pipeline tests

.PHONY: test-lint
test-lint: $(VENV)
	$(VENV)/bin/flake8 .

.PHONY: test-types
test-types: $(VENV)
	. $(VENV)/bin/activate && mypy mentor_pipeline

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


# Runs a shell inside the data processing pipeline dockerfile
.PHONY shell:
shell: docker-image-exists
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

LICENSE:
	@echo "you must have a LICENSE file" 1>&2
	exit 1

LICENSE_HEADER:
	@echo "you must have a LICENSE_HEADER file" 1>&2
	exit 1

.PHONY: license
license: LICENSE LICENSE_HEADER $(VENV)
	$(VENV)/bin/python3 -m licenseheaders -t LICENSE_HEADER --ext py -d bin
	$(VENV)/bin/python3 -m licenseheaders -t LICENSE_HEADER --ext py -d tests
	$(VENV)/bin/python3 -m licenseheaders -t LICENSE_HEADER --ext py -d mentor_pipeline

.PHONY: test-license
test-license: LICENSE LICENSE_HEADER $(VENV)
	$(VENV)/bin/python3 -m licenseheaders -t LICENSE_HEADER --ext py -d bin
	$(VENV)/bin/python3 -m licenseheaders -t LICENSE_HEADER --ext py -d tests --check
	$(VENV)/bin/python3 -m licenseheaders -t LICENSE_HEADER --ext py -d mentor_pipeline --check
