from pyrestcli.fields import IntegerField, CharField, BooleanField

from .resources import AsyncResource, Manager
from .paginators import CartoPaginator


API_VERSION = "v1"
API_ENDPOINT = 'api/{api_version}/imports/'


class FileImportJob(AsyncResource):
    """
    This class provides support for one-time uploading and importing of remote and local files into CARTO
    """
    item_queue_id = CharField()
    id = CharField()
    user_id = CharField()
    table_id = CharField()
    data_type = CharField()
    table_name = CharField()
    state = CharField()
    error_code = IntegerField()
    queue_id = CharField()
    tables_created_count = IntegerField()
    synchronization_id = CharField()
    type_guessing = BooleanField()
    quoted_fields_guessing = BooleanField()
    content_guessing = BooleanField()
    create_visualization = BooleanField()
    visualization_id = CharField()
    user_defined_limits = CharField()
    get_error_text = None
    display_name = CharField()
    success = BooleanField()
    warnings = None
    is_raster = BooleanField()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        id_field = "item_queue_id"

    def __init__(self, url, auth_client):
        """
        :param auth_client: Client to make authorized requests (currently only APIKeyAuthClient is supported)
        :param url: URL can be a pointer to a remote location or a path to a local file
        :return:
        """
        if url.startswith("http"):
            self.url = url
            self.files = None
        else:
            self.url = None
            self.files = {'file': open(url, 'rb')}

        super(FileImportJob, self).__init__(auth_client)

    def run(self, **import_params):
        """
        Actually creates the import job on the CARTO server
        :param import_params: To be send to the Import API, see CARTO's docs on Import API for an updated list of accepted params
        :return:
        """
        if self.url:
            import_params["url"] = self.url

        super(FileImportJob, self).run(params=import_params, files=self.files)
        self.id_field = "id"


class FileImportJobManager(Manager):
    resource_class = FileImportJob
    json_collection_attribute = "imports"
    paginator_class = CartoPaginator

    def filter(self):
        """
        Get a filtered list of file imports
        :return: A list of file imports, with only the id set (you need to refresh them if you want all the attributes to be filled in)
        """
        response = self.send(self.get_collection_endpoint(), "get")
        resource_ids = self.client.get_response_data(response, self.Meta.parse_json)[self.json_collection_attribute] if self.json_collection_attribute is not None else self.client.get_response_data(response, self.Meta.parse_json)

        resources = []

        for resource_id in resource_ids:
            try:
                resource = self.resource_class(self.client)
            except (ValueError, TypeError):
                continue
            else:
                setattr(resource, resource.Meta.id_field, resource_id)
                resources.append(resource)

        return resources

    def create(self, url, **kwargs):
        """
        Create a file import on the server
        :param url: URL can be a pointer to a remote location or a path to a local file
        :params kwargs: Attributes (field names and values) of the new resource
        """
        resource = self.resource_class(url, self.client)
        resource.update_from_dict(kwargs)
        resource.save(force_create=True)

        return resource
