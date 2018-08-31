# Run Unittests
.PHONY: test
test:
	nosetests

# run flake8
.PHONY: lint
lint:
	flake8 --exclude=_dumpster,_not* --ignore=D200,D205,D400,D401,E731

,PHONY: test-docker
test-docker:
	docker-compose run --rm test-pyprom