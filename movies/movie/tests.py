from django.test import TestCase
from .models import Movie, MovieGenres, MovieLanguages, User, Actors, Rating


class MovieModelTest(TestCase):
    def setUp(self):
        self.genre_action = MovieGenres.objects.create(genre_id=1, genre="Action")
        self.genre_sci_fi = MovieGenres.objects.create(genre_id=2, genre="Sci-Fi")
        self.language_english = MovieLanguages.objects.create(language_id=1, language="English")
        self.language_french = MovieLanguages.objects.create(language_id=2, language="French")
        self.user = User.objects.create(username="testuser")
        self.actor_leo = Actors.objects.create(actor_name="Leonardo DiCaprio")
        self.actor_kate = Actors.objects.create(actor_name="Kate Winslet")

        # Create the movie instance
        self.movie = Movie.objects.create(
            movie_id=1,
            original_title="Inception",
            overview="A mind-bending thriller about dream invasion.",
            slug="inception",
            tagline="Dreams feel real while we're in them.",
            year=2010,
            movie_url="https://example.com/inception",
        )

        self.movie.genres.add(self.genre_action, self.genre_sci_fi)
        self.movie.languages.add(self.language_english, self.language_french)
        self.movie.actors.add(self.actor_leo, self.actor_kate)

        Rating.objects.create(user=self.user, movie=self.movie, rating=5)

    def test_movie_creation(self):
        self.assertEqual(self.movie.original_title, "Inception")
        self.assertEqual(self.movie.genres.count(), 2)
        self.assertEqual(self.movie.languages.count(), 2)
        self.assertEqual(self.movie.actors.count(), 2)
        self.assertEqual(self.movie.ratings.count(), 1)
