# Multi-stage build for MkDocs static site
FROM python:3.12-slim as builder

# Install build dependencies
RUN pip install --no-cache-dir mkdocs-material mkdocs-git-revision-date-localized-plugin

# Set work directory
WORKDIR /app

# Copy MkDocs configuration and documentation
COPY mkdocs.yml .
COPY docs/ ./docs/

# Build the static site
RUN mkdocs build

# Production stage - serve with nginx
FROM nginx:alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy built site from builder stage
COPY --from=builder /app/site /usr/share/nginx/html

# Copy nginx configuration
COPY docs-site/nginx.conf /etc/nginx/conf.d/default.conf

# OpenShift-compatible setup: prepare for arbitrary user ID
RUN chmod -R g+rwX /var/cache/nginx /var/run /var/log/nginx /usr/share/nginx/html /etc/nginx/conf.d && \
    chmod g+rw /var/cache/nginx /var/run /var/log/nginx

# Don't set a specific user - let OpenShift assign arbitrary UID
# OpenShift will run as non-root with a random UID in the root group (GID 0)

# Expose port 8080 (OpenShift compatible)
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]