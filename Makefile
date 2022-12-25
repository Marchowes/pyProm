# Run Unittests
.PHONY: test
test:
	nosetests -v

# run flake8
.PHONY: lint
lint:
	flake8 --exclude=_dumpster,_not* --ignore=D200,D205,D400,D401,E731

.PHONY: test-docker
test-docker:
	docker-compose run --rm test-pyprom

.PHONY: pyprom-docker
pyprom-docker:
	docker-compose run --rm pyprom

.PHONY: pyprom-dev
pyprom-dev:
    docker-compose run --rm pyprom-dev

.PHONY: pyprom-dev-build
pyprom-dev-build:
    docker build pyprom-dev