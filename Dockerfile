# Dockerfile for GCP Cloud Run
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache python3 py3-pip git gcc musl-dev linux-headers python3-dev

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Node.js dependencies (skip husky in production)
RUN npm ci --only=production --ignore-scripts

# Install Python dependencies
RUN pip3 install --break-system-packages -r requirements.txt

# Copy application code
COPY . .

RUN rm -f gcp_credentials.json *.pem *.key *.p12 *.pfx

# Create necessary directories
RUN mkdir -p temp/repos temp/contexts app/context public/context

# Set permissions
RUN chmod +x scripts/*.py scripts/*.sh

# Install curl for health check
RUN apk add --no-cache curl

# Build the application
RUN npm run build

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/api/health || exit 1

# Start the application
CMD ["sh","-c","npm start -- -H 0.0.0.0 -p ${PORT:-8080}"]