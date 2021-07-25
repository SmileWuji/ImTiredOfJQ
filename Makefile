.PHONY: clean test dependency
.DEFAULT_GOAL := test
export PYTHONPATH := $(CURDIR)/src/

test: clean
	python -m pytest tst/

clean:
	find . -type f -name '*.pyc' -delete

dependency:
	@pip install pytest
