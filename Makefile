.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 matriz tests

test:
	python setup.py test

test-all:
	tox

coverage:
	coverage run --source matriz setup.py test
	coverage report -m
	# Uncomment the following lines in the Makefile 
	# to generate an html report and open it in the browser
	# coverage html
	# xdg-open htmlcov/index.html

docs:
	rm -f docs/matriz.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ matriz
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean dist
	twine upload dist/matriz* -r stressfm

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist
