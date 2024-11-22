# Use the official Python image from the Docker Hub
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Install the requirements
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader punkt


COPY movies/data /app/movies/data
COPY movies/forum /app/movies/forum
COPY movies/menu /app/movies/menu
COPY movies/playlist /app/movies/playlist
COPY movies/movies /app/movies/movies
COPY movies/static /app/movies/static
COPY movies/templates /app/movies/templates
COPY movies/users /app/movies/users
COPY movies/chroma_db.py /app/movies/chroma_db.py
COPY movies/generate_embeddings.py /app/movies/generate_embeddings.py
COPY movies/manage.py /app/movies/manage.py
COPY movies/recommendations.py /app/movies/recommendations.py
COPY movies/word2vec.model /app/movies/word2vec.model

COPY movies/movie/migrations /app/movies/movie/migrations
COPY movies/movie/static /app/movies/movie/static
COPY movies/movie/templates /app/movies/movie/templates
COPY movies/movie/__init__.py /app/movies/movie/__init__.py
COPY movies/movie/admin.py /app/movies/movie/admin.py
COPY movies/movie/apps.py /app/movies/movie/apps.py
COPY movies/movie/models.py /app/movies/movie/models.py
COPY movies/movie/tests.py /app/movies/movie/tests.py
COPY movies/movie/urls.py /app/movies/movie/urls.py
COPY movies/movie/views.py /app/movies/movie/views.py

#COPY movies /apps/movies
COPY populate_database /app/populate_database

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=movies.settings

# Expose the port the app runs on
EXPOSE 8000

# Run the Django development server
CMD ["python", "movies/manage.py", "runserver", "0.0.0.0:8000"]
