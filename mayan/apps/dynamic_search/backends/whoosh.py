from collections import Iterable
import logging
from pathlib import Path

from whoosh import fields
from whoosh import qparser
from whoosh.filedb.filestore import FileStorage

from django.conf import settings
from django.db import models

from colorful.fields import RGBColorField

from mayan.apps.common.exceptions import ResolverPipelineError
from mayan.apps.common.utils import ResolverPipelineModelAttribute

from ..classes import SearchBackend, SearchField, SearchModel

DEFAULT_SEARCH_LIMIT = 100
DJANGO_TO_WHOOSH_FIELD_MAP = {
    models.AutoField: {'field': fields.ID(stored=True), 'transformation': str},
    models.CharField: {'field': fields.TEXT},
    models.TextField: {'field': fields.TEXT},
    models.UUIDField: {'field': fields.TEXT, 'transformation': str},
    RGBColorField: {'field': fields.TEXT},
}
INDEX_DIRECTORY_NAME = 'whoosh'
logger = logging.getLogger(name=__name__)


class Sieve:
    @staticmethod
    def flatten_list(value):
        for item in value:
            if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                yield from Sieve.flatten_list(value=item)
            else:
                yield item

    @staticmethod
    def function_return_same(value):
        return value

    def __init__(self, search_backend, search_model):
        self.field_map = search_backend.get_resolved_field_map(
            search_model=search_model
        )

    def process_instance(self, instance):
        result = {}
        for field in self.field_map:
            try:
                value = ResolverPipelineModelAttribute.resolve(
                    attribute=field, obj=instance
                )
                try:
                    value = ''.join(Sieve.flatten_list(value))
                except TypeError:
                    """Value is not a list"""
            except ResolverPipelineError:
                """Not fatal"""
            else:
                result[field] = self.field_map[field].get(
                    'transformation', Sieve.function_return_same
                )(value)

        return result


class WhooshSearchBackend(SearchBackend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.index_path = Path(settings.MEDIA_ROOT, INDEX_DIRECTORY_NAME)
        self.index_path.mkdir(exist_ok=True)

        self.search_limit = self.kwargs.get(
            'search_limit', DEFAULT_SEARCH_LIMIT
        )

        #for search_model in SearchModel.all():
        #    self.index_search_model(search_model=search_model)
        #search_model=SearchModel.get(name='documents.Document')
        #self.index_search_model(search_model=search_model)

    def initialize(self):
        self.search_model_sieves = {}
        for search_model in SearchModel.all():
            self.search_model_sieves[search_model] = Sieve(
                search_backend=self, search_model=search_model
            )

    def _search(self, query_string, search_model, user, global_and_search=False):
        index = self.get_index(search_model=search_model)

        id_list = []
        with index.searcher() as searcher:
            search_string = []

            if 'q' in query_string:
                # Emulate full field set search
                for search_field in self.get_search_model_fields(search_model=search_model):
                    search_string.append(
                        '{}:({})'.format(search_field.get_full_name(), query_string['q'])
                    )
            else:
                for key, value in query_string.items():
                    if value:
                        search_string.append(
                            '{}:({})'.format(key, value)
                        )

            global_logic_string = ' AND ' if global_and_search else ' OR '
            search_string = global_logic_string.join(search_string)

            logger.debug('search_string: %s', search_string)

            parser = qparser.QueryParser(
                fieldname='_', schema=index.schema
            )
            parser.remove_plugin_class(cls=qparser.WildcardPlugin)
            parser.add_plugin(pin=qparser.PrefixPlugin())
            query = parser.parse(text=search_string)
            results = searcher.search(q=query, limit=self.search_limit)

            for result in results:
                id_list.append(result['id'])

        return search_model.model.objects.filter(id__in=id_list).distinct()

    def get_index(self, search_model):
        storage = self.get_storage()

        schema = self.get_search_model_schema(search_model=search_model)

        try:
            index = storage.open_index(
                indexname=search_model.get_full_name()
            )
        except Exception:
            index = storage.create_index(
                schema, indexname=search_model.get_full_name()
            )

        return index

    def get_resolved_field_map(self, search_model):
        result = {}
        for search_field in self.get_search_model_fields(search_model=search_model):
            whoosh_field_type = DJANGO_TO_WHOOSH_FIELD_MAP.get(
                search_field.get_model_field().__class__
            )
            if whoosh_field_type:
                result[search_field.get_full_name()] = whoosh_field_type
            else:
                logging.warning(
                    'unknown field type "%s" for model "%s"',
                    search_field.get_full_name(),
                    search_model.get_full_name()
                )

        return result

    def get_search_model_fields(self, search_model):
        result = search_model.search_fields.copy()
        result.append(
            SearchField(search_model=search_model, field='id', label='ID')
        )
        return result

    def get_search_model_schema(self, search_model):
        field_map = self.get_resolved_field_map(search_model=search_model)
        schema_kwargs = {key: value['field'] for key, value in field_map.items()}
        return fields.Schema(**schema_kwargs)

    def get_storage(self):
        return FileStorage(path=self.index_path)

    def index_instance(self, instance):
        search_model = SearchModel.get_for_model(instance=instance)
        index = self.get_index(search_model=search_model)

        writer = index.writer()
        kwargs = self.search_model_sieves[search_model].process_instance(
            instance=instance
        )
        writer.delete_by_term('id', str(instance.pk))
        writer.add_document(**kwargs)
        writer.commit()

    def index_search_model(self, search_model):
        index = self.get_index(search_model=search_model)

        # Clear the model index
        self.get_storage().create_index(
            index.schema, indexname=search_model.get_full_name()
        )

        for instance in search_model.model._meta.default_manager.all():
            self.index_instance(instance=instance)
