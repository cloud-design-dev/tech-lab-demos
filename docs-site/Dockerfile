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

# Create nginx user and set permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Switch to non-root user
USER nginx

# Expose port 8080 (OpenShift compatible)
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]