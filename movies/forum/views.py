from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect

from movie.models import Movie,Rating
from .models import Review
from .forms import ReviewForm

def forum_menu(request):
    return render(request,'forum/forum_menu.html')


@login_required
def write_review(request, movie_id):
    movie = get_object_or_404(Movie, movie_id=movie_id)

    # Check if the user has already submitted a review for this movie
    existing_review = Review.objects.filter(user=request.user, movie=movie).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check if a review already exists and update it or create a new one
            if existing_review:
                existing_review.review = form.cleaned_data['review']
                existing_review.save()
            else:
                # Create a new review
                Review.objects.create(
                    user=request.user,
                    movie=movie,
                    review=form.cleaned_data['review']
                )
            return redirect('show_movie', movie_id=movie.movie_id)  # Redirect to the movie detail page or wherever you want
    else:
        form = ReviewForm()
        # If the user has already reviewed the movie, prepopulate the form with their existing review
        if existing_review:
            form.fields['review'].initial = existing_review.review

    return render(request, 'forum/write_review.html', {'form': form, 'movie': movie})


def view_single_review(request, review_id):

    review = Review.objects.get(id__exact=review_id)

    movie_id = review.movie_id
    user = review.user

    movie = Movie.objects.get(movie_id__exact=movie_id)
    rating = Rating.objects.filter(user=user, movie=movie).first()

    rating = rating.rating if rating else "No Rating"


    genres = movie.genres.all()
    genres_in_movie = genres.values_list('genre', flat=True)

    languages = movie.languages.all()
    language_in_movie = languages.values_list('language', flat=True)

    context = {
        'movie':movie,
        'review':review,
        'genres':genres_in_movie,
        'languages':language_in_movie,
        'rating':rating
    }

    return render(request,'forum/view_single_review.html',context)


def view_reviews(request):

    reviews = Review.objects.all()

    context = {
        "reviews":reviews
    }

    return render(request,'forum/view_reviews.html',context)
