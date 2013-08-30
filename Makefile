
PY=python
PIP=pip

all:
	$(PY) setup.py build_ext --inplace

test:
	nosetests

requirements:
	$(PIP) install -r requirements.txt

clean: build
	rm -r build/
	find . -name *.so -delete
