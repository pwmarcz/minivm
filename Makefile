.PHONY: all
all: test

.PHONY: test
test:
	python3 -m unittest discover -p '*.py' -v

examples/password.bc: spoilers/password.asm
	./mini as $< $@
