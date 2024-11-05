# Search and Recommendation System with Django

## Abstract
This is a Django web app that allows user searching for their favorite movies.
Also, for each movie system will provide up to 10 recommendations. 

Also, users can create their playlist and based on movies in playlist they will get up to 10 recommendations. 

Right now database, which is SQLite, contains around 25k movies.

<img width="1300" alt="teaser" src="./figure/sample.PNG">

## Data

We used movies data from Kaggle:

```
https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset
```

SQLite is used to store it. 

## Methodology

1. Our recommendation system is content based - it makes predictions based only on the movies you selected.
2. As a baseline we are using cosine similarity. Each movie has its own numeric representation (vector) which is stored in SQLite (movie metadata table).
3. Also, we are producing additional text features for our model with Word2Vec. train_embedding is the module to train Word2Vec on current movies' data.
4. Finally, we concatenate the features and call cosine similarity measure for each movie pair. Then we sort by similarity measure and select top 10.
5. We store recommendation in movies_cache folder (FileBasedCache).
6. We also have a chatbot assistant to help users to find in natural help, not only by name.

## Project Set Up

You can clone rep from GitHub:

```
git clone https://github.com/Maestro-111/movies-search-system.git
cd movies-search-system
```

## Data Set Up

Script to normalize Kaggle data currently is not uploaded.
Instead, all tables, imported in xlsx, are present in "movies/data" folder.

We need to create tables first. You'll need to:

1) Create venv (virtual environment), activate venv, install requirements and go to movies directory.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt 
cd movies
```

2) Run makemigrations

```
python manage.py makemigrations
```

3) Run migrate

```
python manage.py migrate
```

4) Finally, we populate the database. Deactivate current venv, go to populate_database module and activate its venv.

```
deactivate
cd ..
cd populate_database
venv\Scripts\activate
```

Run main.py to populate created tables

```
python main.py
```

## How to Run:

After you populated database, go back to movies dir
```
deactivate
cd ..
venv\Scripts\activate
cd movies
```

Create embedding for the movies. App's going to use them later for requests in natural language

```
python generate_embeddings.py
```

Execute command:

```
python manage.py runserver
```


## Docker Set up

1) Create an image:

```
docker build -t my-django-app .
```

2) Run container 

```
docker run -p 8000:8000 my-django-app
```

3) Get id of your container 

```
dokcer ps 
```

4) start a shell session in container

```
docker exec -it <container_id> /bin/bash
```

5) run migrations and populate database script

```
cd movies
python manage.py makemigrations
python manage.py migrate
cd ..
cd populate_database
python main.py
exit()
```


## TO DO

1. Tweak the final equation with rating (recommendations.py produce_recommendations func) 
2. Updating Forum Section.
3. Better front-end (?)
4. Help user to search with indirect request (continue)
5. Configure .env








