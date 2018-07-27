# Run Unittests
.PHONY: test
test:
	nosetests

# run flake8
.PHONY: lint
lint:
	flake8 --exclude=_dumpster --ignore=D200,D205,D400,D401,E731
