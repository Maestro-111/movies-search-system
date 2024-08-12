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

(Docker set up is coming up...)

Script to normalize Kaggle data currently is not uploaded.
Instead, all tables, imported in xlsx, are present in "data" folder.

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

python populate_movies
python populate_metadata
python populate_genres
python populate_language
python populate_movie_genres
python populate_languages
```


## TO DO
1. Improve recommendations for user.
2. Automate scripts execution for populating the database (after pull, run migs in docker and populate database script).
3. Integrate rating into recommendations. 









