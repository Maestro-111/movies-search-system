# Base Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user for development
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader punkt

# Install development tools
RUN pip install --no-cache-dir \
    black \
    pylint \
    pytest \
    django-debug-toolbar

# Copy the project
COPY movies/ /app/movies/
COPY LDA/ /app/LDA/
COPY .env /app/
COPY Makefile /app/
COPY docker/local/entrypoint.sh /app/

RUN chmod +x entrypoint.sh
RUN chown -R $USERNAME:$USERNAME /app

# Switch to non-root user
USER $USERNAME

# Expose port
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]