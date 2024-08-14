# Search and Recommendation System with Django

## Abstract
This is a Django web app that allows user searching for their favorite movies.
Also, for each movie system will provide up to 10 recommendations. 
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
2. As a baseline we are using cosine similarity. Each movie has its own numeric representation (vector) which is stored in SQLite.
3. We are reducing dim of movie numeric representation with PCA. 
4. Also, we are producing additional text features for our model with Word2Vec. train_embedding is the module to train Word2Vec on current movies' data.
5. Finally, we concatenate the features and call cosine similarity measure for each movie pair. Then we sort by sim measure and select top 10.

## Data Set Up

Script to normalize Kaggle data currently is not uploaded.
Instead, all tables, imported in xlsx, are present in "movies/data" folder.

We need to create tables first. You'll need to:

1) Activate vend and go to movies directory.

```
venv\Scripts\activate
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

4) Finally, we populate the database. Run the scripts in populate_database in the following order:

```
deactivate
cd ..
cd populate_database
venv\Scripts\activate

python main.py
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
1. Improve recommendations for user.
2. Integrate rating into recommendations. 
3. Updating Forum Section.









