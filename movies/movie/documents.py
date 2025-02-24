from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Q as ESQ
from .models import Movie


@registry.register_document
class MovieDocument(Document):
    class Meta:
        id_field = 'movie_id'

    class Index:
        name = 'movies'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'multilingual_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': [
                            'lowercase',
                            'asciifolding'  # Handles diacritics and special characters
                        ]
                    }
                }
            }
        }

    original_title = fields.TextField(
        analyzer='multilingual_analyzer',
        search_analyzer='multilingual_analyzer'
    )

    class Django:
        model = Movie
        fields = [
            'movie_id',
            'overview',
        ]