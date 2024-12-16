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

### Search

1) We use PostgresSQL to store the data
2) Users have 3 ways to search for a movie. 

   1) By title. System will use PostgresSQL full text search to look for the best match based on a title.
   2) In a natural language by using custom chat box. For that we store text embeddings of each movie in ChromaDB client.
   3) By movie poster. For that we store image embeddings of each movie poster in ChromaDB client.
    
    The most accurate way is #1.

### Recommendations

1) Our system produces content based recommendations. It means it will recommend movies only based on the choice of previosuly selected movies.
2) We use simple cosine similarity equation modified to accept more inputs such as ratings.


## Project Set Up

You can clone rep from GitHub:

```
git clone https://github.com/Maestro-111/movies-search-system.git
cd movies-search-system
```



## Docker Set up

It's convinient to use docker to  get all packages/dependencies set up together.

1) Create a docker compose:

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
