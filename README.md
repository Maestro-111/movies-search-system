# Search and Recommendation System with Django

## Abstract
This is a Django web app that allows user searching for their favorite movies.
Also, for each movie system will provide up to 10 produce_recommendations. 
Right now database, which is SQLite, contains around 25k movies. 

<img width="1300" alt="teaser" src="./figure/sample.PNG">

## Data

We used movies data from Kaggle:

```
https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset
```

SQLite is used to store it. Currently, script to normalize data and populate database is not available.

## Methodology

1. Our recommendation system is content based - it makes predictions based only on movies you selected.
2. As a baseline we are using dot product similarity. Each movie has its own numeric representation (vector) which is stored in SQLite.
3. We are reducing dim of movie numeric representation with PCA. 
4. Also, we are producing additional text features for our model with Word2Vec. train_embedding is module to train Word2Vec on current movies' data.

## Set Up
Currently, set up for this project is not supported

## TO DO
1. Improve recommendations for user.
2. Add set up instructions and data.









