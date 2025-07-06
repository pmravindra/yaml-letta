# Contributing to yaml-letta

Thank you for your interest in contributing to yaml-letta! 

## Development Setup

### Using Docker (Recommended)

1. Clone the repository
2. Run tests:
   ```bash
   make test
   ```

3. For interactive development:
   ```bash
   make test-interactive
   ```

### Local Development

1. Install dependencies:
   ```bash
   pip install -e .
   pip install -r test-requirements.txt
   ```

2. Run tests:
   ```bash
   pytest tests/
   ```

## Running Tests

All tests must pass before submitting a PR:

```bash
# Using Docker
make test

# Or directly
docker-compose run --rm test
```

## Code Style

- Use type hints where possible
- Follow PEP 8 guidelines
- Add docstrings to all public functions and classes

## Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Adding New Features

When adding new features:
1. Update the relevant YAML examples
2. Add comprehensive tests
3. Update documentation if needed