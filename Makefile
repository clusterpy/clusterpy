
PY=python
PIP=pip

all:
	$(PY) setup.py build_ext --inplace

requirements:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements2.txt

clean: build
	rm -r build/
	find . -name *.so -delete
