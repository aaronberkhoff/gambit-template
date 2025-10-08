.PHONY: all clean stubs stubs_clean build

STUB_DIR := python/gambit_template

build:
	@echo "Building project..."
	python scripts/build.py

stubs:
	@echo "Generating stubs..."
	python scripts/make_stubs.py gambit_template

all: build stubs

clean:
	@echo "Cleaning build and stubs..."
	python scripts/build.py --clean

stubs_clean:
	@echo "Cleaning stubs..."
	rm -rf $(STUB_DIR)
