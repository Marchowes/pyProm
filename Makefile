PACKAGE=pyProm

.PHONY: clean

init:
	pip install -r test-requirements.txt

style:
	flake8 $(PACKAGE)

ci: init style

publish:
	python setup.py register
	python setup.py sdist upload
	rm -fr build dist .egg $(PACKAGE).egg-info

clean:
	rm -rf $(PACKAGE)/*.pyc
	rm -rf $(PACKAGE)/__pycache__
	rm -rf tests/__pycache__
	rm -rf $(PACKAGE).egg-info