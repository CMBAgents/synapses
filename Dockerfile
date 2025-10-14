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

# Install Node.js dependencies (including dev dependencies for build)
RUN npm ci --ignore-scripts

# Install Python dependencies
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p temp/repos temp/contexts public/context

# Set permissions for all Python and shell scripts in subdirectories
RUN find maintenance -name "*.py" -exec chmod +x {} \; && \
    find maintenance -name "*.sh" -exec chmod +x {} \;

# Build the application
RUN npm run build

# Clean up build dependencies to save space
RUN npm prune --production

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