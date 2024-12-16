# Movie Search and Recommendation System

## Abstract
This is a Django web app that allows user searching for their favorite movies.
Also, for each movie system will provide up to 10 recommendations.

Also, users can create their playlist and based on movies in playlist they will get up to 10 recommendations.

Right now database, which is PostgresSQL, contains around 25k movies and related information.

<img width="1300" alt="teaser" src="./figure/sample.png">

## Data

We used movies data from Kaggle:

```
https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset
```

Posters image data:

```
https://www.kaggle.com/datasets/neha1703/movie-genre-from-its-poster?select=MovieGenre.csv
```


PostgresSQL is used to store it.

## Methodology

1. Our recommendation system is content based - it makes predictions based only on the movies you selected.
2. As a baseline we are using cosine similarity. Each movie has its own numeric representation (vector) which is stored in PostgresSQL (movie metadata table).
3. Also, we are producing additional text features for our model with Word2Vec. train_embedding is the module to train Word2Vec on current movies' data.
4. Finally, we concatenate the features and call cosine similarity measure for each movie pair. Then we sort by similarity measure and select top 10.
5. We store recommendation in movies_cache folder (FileBasedCache).
6. We also have a chatbot assistant to help users to find in natural help, not only by name. We calculate embeddings and store them in ChromaDB
7. You can search for a movie by its poster (image) with the help of embeddings built with ResNet. We store image embeddings in ChromaDB as well.

## Project Set Up

You can clone rep from GitHub:

```
git clone https://github.com/Maestro-111/movies-search-system.git
cd movies-search-system
```



## Docker Set up

It's convinient to use docker to  get all packages/dependencies set up together.

1) Create a dokcer compose:

```
docker compose build
docker compose up
```

2) Run migrations from web container

```
cd movies
python manage.py makemigrations
python manage.py migrate
```

3) Populate PostgresSQL (this will take a while...)

```
cd ..
cd populate_databse
python main.py

```

4) Create Embeddings for both images/text

```
cd ..
python generate_text_embeddings.py
python generate_image_embeddings.py
```


## TO DO

1. Updating Forum Section.
2. front-end (cont)
3. Fix .dockerignore issue (e.g. not ignoring sqlite files)
4. Continue updating friends section within users. Final goal is to have more info for recommendations
