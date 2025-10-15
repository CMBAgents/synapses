# Dockerfile for GCP Cloud Run - Optimized for memory
FROM node:18-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    git \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Python dependencies (PyTorch CPU-only pour économiser ~2.5 GB)
RUN pip3 install --break-system-packages --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu && \
    pip3 install --break-system-packages --no-cache-dir -r requirements.txt && \
    find /usr/local -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p temp/repos temp/contexts public/context

# Set permissions for all Python and shell scripts in subdirectories
RUN find maintenance -name "*.py" -exec chmod +x {} \; && \
    find maintenance -name "*.sh" -exec chmod +x {} \;

# Install Node deps, build, et nettoyer DANS LA MÊME COUCHE pour économiser ~500 MB
RUN npm ci --ignore-scripts && \
    npm run build && \
    npm prune --production && \
    rm -rf .next/cache

# Set memory optimization environment variables
ENV NODE_OPTIONS="--max-old-space-size=400"
ENV NEXT_PUBLIC_BASE_URL="https://cmbagent-info-602105671882.europe-west1.run.app"

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/api/health || exit 1

# Start the application
CMD ["sh","-c","npm start -- -H 0.0.0.0 -p ${PORT:-8080}"]