# Makefile for gambit-template

.PHONY: all build clean test install dev lock help stubs stubs_clean

PACKAGE_NAME := gambit_template

# misc directories
STUB_DIR := python/gambit_template
DIST_DIR := dist/
BUILD_DIR := build/
PYTHON_DIR := python/

DIRS := $(DIST_DIR) $(BUILD_DIR) $(STUB_DIR)

dirs: 
	mkdir -p $(DIRS)

# bazel directories
BAZEL_BIN_DIR := bazel-bin/
BAZEL_CPP_DIR := $(BAZEL_BIN_DIR)/cpp
BAZEL_PYTHON_DIR := $(BAZEL_BIN_DIR)/python


# Default target
all: lock build stubs

# Build everything (C++ and Python)
build: dirs
	@echo "Building C++ and Python with Bazel..."
	bazel build //...

	@echo "Copying wheel to $(DIST_DIR)"
	cp -rf $(BAZEL_PYTHON_DIR)/*.whl $(DIST_DIR)

	@echo "Copying python binding .so to $(PYTHON_DIR)"
	cp -rf $(BAZEL_CPP_DIR)/$(PACKAGE_NAME).so $(PYTHON_DIR)
	cp -rf $(BAZEL_CPP_DIR)/$(PACKAGE_NAME).pyd $(PYTHON_DIR)

	@echo "Copying c++ dist to $(BUILD_DIR)"
	cp -rf $(BAZEL_CPP_DIR)/*.a $(BUILD_DIR)

	@echo "Build complete! Wheel at: $(DIST_DIR)/"

# Build only the wheel (no artifact copying)
build-wheel:
	@echo "Building wheel with Bazel..."
	bazel build //python:gambit_template_wheel
	@echo "Wheel built at: bazel-bin/python/gambit_template_wheel.whl"

# Build only C++ library
build-cpp:
	@echo "Building C++ library..."
	bazel build //cpp:all
	@echo "C++ library built"

# Generate stubs for C++ extensions
stubs: build
	@echo "Generating stubs..."
	python scripts/make_stubs.py gambit_template
	@echo "Stubs generated in $(STUB_DIR)"

# Generate/update requirements lock file from pyproject.toml
lock:
	@echo "Updating requirements lock file with UV..."
	@if [ ! -f requirements_lock.txt ]; then \
		echo "Creating initial requirements_lock.txt..."; \
		touch requirements_lock.txt; \
	fi
	bazel run //:requirements
	@echo "Lock file updated: requirements_lock.txt"

# Clean build artifacts
clean: stubs_clean
	@echo "Cleaning build artifacts..."
	rm -rf $(DIST_DIR)
	rm -rf $(BUILD_DIR)
	rm -rf $(PYTHON_DIR)/*.so
	rm -rf $(PYTHON_DIR)/*.pyd
	bazel clean
	@echo "Clean complete"

# Clean only stubs
stubs_clean:
	@echo "Cleaning stubs..."
	rm -rf $(STUB_DIR)/*.pyi
	@echo "Stubs cleaned"

# Deep clean (Bazel + artifacts)
new: clean
	@echo "Deep cleaning..."
	bazel clean --expunge
	rm -rf .venv
	@echo "Deep clean complete"

# Run tests
test:
	@echo "Running tests with Bazel..."
	bazel test //...

# Install in development mode (creates venv with UV)
dev:
	@echo "Setting up development environment with UV..."
	uv sync
	@echo "Development environment ready. Activate with: source .venv/bin/activate"

# Install the built wheel locally
install: build
	@echo "Installing wheel locally..."
	pip install --force-reinstall $(DIST_DIR)/*.whl
	@echo "Installation complete"

# Install for local development with UV (editable mode alternative)
install-dev: dev
	@echo "Installing in development mode..."
	uv pip install -e .
	@echo "Development installation complete"

# Format code
format:
	@echo "Formatting code..."
	uv run black python/
	uv run ruff check --fix python/

# Lint code
lint:
	@echo "Linting code..."
	uv run ruff check python/

# Type check
typecheck:
	@echo "Type checking..."
	uv run mypy python/

# Build distribution (wheel + sdist)
dist: build
	@echo "Preparing distribution..."
	mkdir -p dist/
	cp bazel-bin/python/gambit_template_wheel.whl dist/
	@echo "Distribution ready in dist/"

# Upload to PyPI (requires twine)
upload: dist
	@echo "Uploading to PyPI..."
	uv run twine upload dist/*

# Upload to TestPyPI
upload-test: dist
	@echo "Uploading to TestPyPI..."
	uv run twine upload --repository testpypi dist/*

# Check if tools are installed
check-deps:
	@echo "Checking dependencies..."
	@command -v bazel >/dev/null 2>&1 || { echo "ERROR: bazel is not installed"; exit 1; }
	@command -v uv >/dev/null 2>&1 || { echo "ERROR: uv is not installed"; exit 1; }
	@echo "All required tools are installed"

# Initialize project (first-time setup)
init: check-deps
	@echo "Initializing project..."
	@if [ ! -f pyproject.toml ]; then \
		echo "ERROR: pyproject.toml not found. Please create it first."; \
		exit 1; \
	fi
	@if [ ! -f requirements_lock.txt ]; then \
		touch requirements_lock.txt; \
	fi
	uv sync
	bazel run //:requirements
	@echo "Project initialized successfully"

# ------------------------
# Update template
# ------------------------

update-template:
	@echo "🔄 Fetching latest changes from template (upstream)..."
	git fetch upstream main
	@echo "⚙️  Rebasing your project on top of template..."
	git rebase upstream/main || (echo "⚠️ Rebase conflict! Resolve manually, then run 'git rebase --continue'"; exit 1)
	@echo "✅ Template successfully merged!"

# Help target
help:
	@echo "Gambit Template - Available Make Targets"
	@echo "========================================"
	@echo ""
	@echo "Building:"
	@echo "  make all          - Update lock file, build everything, and generate stubs (default)"
	@echo "  make build        - Build C++ library and Python wheel (copies to dist/)"
	@echo "  make build-wheel  - Build only Python wheel (no artifact copying)"
	@echo "  make build-cpp    - Build only C++ library"
	@echo "  make stubs        - Generate type stubs for C++ extensions"
	@echo "  make lock         - Update requirements_lock.txt from pyproject.toml"
	@echo "  make dist         - Prepare distribution packages"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Set up development environment with UV"
	@echo "  make install      - Install built wheel locally"
	@echo "  make install-dev  - Install in development mode"
	@echo "  update_template   - Updates the upstream template
	@echo ""
	@echo "Quality:"
	@echo "  make test         - Run tests with Bazel"
	@echo "  make format       - Format code with black and ruff"
	@echo "  make lint         - Lint code with ruff"
	@echo "  make typecheck    - Type check with mypy"
	@echo ""
	@echo "Distribution:"
	@echo "  make upload       - Upload to PyPI"
	@echo "  make upload-test  - Upload to TestPyPI"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - Clean build artifacts (calls build.py --clean)"
	@echo "  make clean-all    - Deep clean including Bazel cache"
	@echo "  make stubs_clean  - Clean only type stubs"
	@echo "  make init         - Initialize project (first-time setup)"
	@echo "  make check-deps   - Check if required tools are installed"
	@echo "  make help         - Show this help message"