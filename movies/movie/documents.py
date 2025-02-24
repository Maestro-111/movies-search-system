from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Movie


@registry.register_document
class MovieDocument(Document):
    original_title = fields.TextField()
    overview = fields.TextField()

    class Index:
        name = 'movies'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Movie  # The model associated with this Document

        fields = [
            'movie_id',
            'original_title',
            'overview',
        ]