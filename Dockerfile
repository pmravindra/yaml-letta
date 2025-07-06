FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .
COPY test-requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r test-requirements.txt

# Copy all necessary files for setup.py
COPY README.md .
COPY setup.py .
COPY yaml-letta/ ./yaml-letta/
COPY tests/ ./tests/
COPY pytest.ini .

# Install the library in development mode
RUN pip install -e .

# Create symlink for package name mapping
RUN ln -s /app/yaml-letta /app/yaml_letta

# Default command runs tests
CMD ["python", "-m", "pytest", "tests/", "-v"]