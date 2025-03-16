# Nix show flake
default:
    nix flake show

# Check the flake
check:
    nix flake check

# Install pre-commit hooks
pre-commit:
    pre-commit install

# Lint with ruff
lint:
    ruff check .
    ruff format .

# Run tests
test:
    pytest -s -v
