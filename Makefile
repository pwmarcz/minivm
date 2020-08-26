.PHONY: all
all: test

.PHONY: test
test:
	python3 -m unittest discover -p '*.py' -v
