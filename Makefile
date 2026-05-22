# Simple Makefile wrapper for the Python-based mini C compiler.
# On Windows use:  python src/main.py input/test_all.c

PY      ?= python
SRC      = src/main.py
INPUT   ?= input/sample.c

.PHONY: all run install clean

all: run

install:
	$(PY) -m pip install -r requirements.txt

run:
	$(PY) $(SRC) $(INPUT)

clean:
	rm -rf src/__pycache__ output/*.txt output/*.asm parser.out parsetab.py
