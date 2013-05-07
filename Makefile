
PY=python

all:
	$(PY) setup.py build_ext --inplace

clean: build
	rm -r build/
	find . -name *.so -delete
