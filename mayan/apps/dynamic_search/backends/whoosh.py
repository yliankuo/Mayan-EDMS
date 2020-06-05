from collections import Iterable
import logging

from whoosh import fields
from whoosh import qparser
from whoosh.filedb.filestore import FileStorage

from django.apps import apps
from django.db import models

from colorful.fields import RGBColorField

from mayan.apps.common.exceptions import ResolverPipelineError
from mayan.apps.common.utils import ResolverPipelineModelAttribute, resolve_attribute

from ..classes import SearchBackend, SearchField

DJANGO_TO_WHOOSH_FIELD_MAP = {
    models.AutoField: fields.ID(stored=True),
    models.CharField: fields.TEXT,
    models.TextField: fields.TEXT,
    models.UUIDField: fields.TEXT,
    RGBColorField: fields.TEXT,
}
INDEX_DIRECTORY = '/tmp/indexdir'
SEARCH_LIMIT = 100
logger = logging.getLogger(name=__name__)


class WhooshSearchBackend(SearchBackend):
    @staticmethod
    def flatten_list(value):
        for item in value:
            if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                yield from WhooshSearchBackend.flatten_list(value=item)
            else:
                yield item

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from ..classes import SearchModel

        #for search_model in SearchModel.all():
        #    self.index_search_model(search_model=search_model)
        #search_model=SearchModel.get(name='documents.Document')
        #self.index_search_model(search_model=search_model)

    def index_search_model(self, search_model):
        index = self.get_index(search_model=search_model)

        # Clear the model index
        self.get_storage().create_index(index.schema, indexname=search_model.get_full_name())

        try:
            writer = index.writer()
        except Exception as exception:
            logger.error('error instantiating index writer; %s', exception)

            index_fields = []
            for search_field in self.get_search_model_fields(search_model=search_model):
                if search_field.get_full_name() in index.schema:
                    index_fields.append(search_field.get_full_name())

            for instance in search_model.model._meta.default_manager.all():
                kwargs = {}

                for search_field in index_fields:
                    try:
                        value = ResolverPipelineModelAttribute.resolve(
                            attribute=search_field, obj=instance
                        )
                        try:
                            value = ''.join(WhooshSearchBackend.flatten_list(value))
                        except TypeError:
                            """Value is not a list"""

                    except ResolverPipelineError:
                        """Not fatal"""
                    else:
                        kwargs[search_field] = value

                writer.add_document(**kwargs)

            writer.commit()

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

    def get_search_model_fields(self, search_model):
        result = search_model.search_fields.copy()
        result.append(
            SearchField(search_model=search_model, field='id', label='ID')
        )
        return result

    def get_search_model_schema(self, search_model):
        kwargs = {}
        for search_field in self.get_search_model_fields(search_model=search_model):
            whoosh_field_type = DJANGO_TO_WHOOSH_FIELD_MAP.get(
                search_field.get_model_field().__class__
            )
            if whoosh_field_type:
                kwargs[search_field.get_full_name()] = whoosh_field_type
            else:
                logging.warning(
                    'unknown field type "%s" for model "%s"',
                    search_field.get_full_name(),
                    search_model.get_full_name()
                )

        return fields.Schema(**kwargs)

    def get_storage(self):
        return FileStorage(INDEX_DIRECTORY)

    def search(self, query_string, search_model, user, global_and_search=False):
        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )

        index = self.get_index(search_model=search_model)

        id_list = []
        with index.searcher() as searcher:
            search_string = []

            if 'q' in query_string:
                # Emulate full field set search
                for search_field in self.get_search_model_fields(search_model=search_model):
                    search_string.append(
                        '{}:{}'.format(search_field.get_full_name(), query_string['q'])
                    )
            else:
                for key, value in query_string.items():
                    # TODO: Remove _match_all in parent class
                    if value and key != '_match_all':
                        search_string.append(
                            '{}:{}'.format(key, value)
                        )

            global_logic_string = ' AND ' if global_and_search else ' OR '
            search_string = global_logic_string.join(search_string)

            logger.debug('search_string: ', search_string)

            parser = qparser.QueryParser('label', index.schema)
            parser.remove_plugin_class(qparser.WildcardPlugin)
            parser.add_plugin(qparser.PrefixPlugin())
            query = parser.parse(search_string)
            results = searcher.search(query, limit=SEARCH_LIMIT)

            for result in results:
                id_list.append(result['id'])

        queryset = search_model.model.objects.filter(id__in=id_list).distinct()

        #TODO: Move to parent class
        if search_model.permission:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=search_model.permission, queryset=queryset,
                user=user
            )

        return queryset
