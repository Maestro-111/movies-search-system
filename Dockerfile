# Use the official Python image from the Docker Hub
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Install the requirements
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader punkt

# Copy the entire project
COPY entrypoint.sh /app/
COPY movies /app/movies
COPY populate_database /app/populate_database
COPY .env /app/

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=movies.settings

# Expose the port the app runs on
EXPOSE 8000

# Create an entrypoint script
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
