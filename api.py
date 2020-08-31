from flask_restx import Api, Namespace, Resource, inputs, fields

from forms import ApiInputValidation as iv
from crud import CRUD
from models import ApiItem, Endpoint
from schemas import api_schema, apis_schema, endpoint_schema, endpoints_schema, field_schema
from extensions import csrf
from config import Globals

api = Api(
    title='CRUD API',
    version='1.0',
    description='API for CRUD operations',
    doc='/swagger',
    validate=True,
    prefix='/api',
    decorators=[csrf.exempt]
)

apis_ns = Namespace('apis', 'API items CRUD operations')
api.add_namespace(apis_ns)

@apis_ns.route('/')
class Apis(Resource):
    get_parser = api.parser()
    get_parser.add_argument('count', type=inputs.boolean, required=False)
    get_parser.add_argument('tags', type=str, required=False)
    get_parser.add_argument('page', type=int, required=False)
    @apis_ns.expect(get_parser)
    @apis_ns.doc(description="Get the count or a list of API items by query", params={
        'count': "A boolean. If True returns just the count of all APIs.",
        'page': "The requested page of API items (page 1 by default).",
        'tags': "Search APIs by tags."
    })
    def get(self):
        args = self.get_parser.parse_args()
        count = args.get('count')
        page = args.get('page')
        tags = args.get('tags')
        if count:
            return JsonMethods.get_apis_count()
        return JsonMethods.get_apis(tags=tags, page=page)

    post_parser = api.parser()
    post_parser.add_argument('label', type=iv.str_validation(max=80), required=True)
    post_parser.add_argument('url', type=iv.url_validation(type='endpoint'), required=True)
    post_parser.add_argument('description', type=iv.str_validation(max=400), required=False)
    post_parser.add_argument('tags', type=iv.str_validation(max=400), required=False)
    @apis_ns.doc(description='Add an API', params={
        'label': 'The label of the API. (80 characters max)',
        'url': 'The root endpoint of the web Api: http://www.example.com/api.',
        'description': 'A short description of the API (400 characters max)',
        'tags': 'List of tags to help the search later. (400 characters max)'
    })
    @apis_ns.expect(post_parser)
    def post(self):
        args = self.post_parser.parse_args()
        label = args.get('label')
        url = args.get('url')
        description = args.get('description')
        tags = args.get('tags')
        return JsonMethods.add_api(label, url, description=description, tags=tags)

@apis_ns.route('/<int:id>')
class ApiItems(Resource):
    @apis_ns.doc(description="Get an API item by id", params={
        'id': "The id of the API"
    })
    def get(self, id):
        return JsonMethods.get_api(id)

    patch_parser = api.parser()
    patch_parser.add_argument('label', type=iv.str_validation(max=80), required=False)
    patch_parser.add_argument('url', type=iv.url_validation(type='endpoint'), required=False)
    patch_parser.add_argument('description', type=iv.str_validation(max=400), required=False)
    patch_parser.add_argument('tags', type=iv.str_validation(max=400), required=False)
    @apis_ns.doc(description='Edit an API', params={
        'id': 'The api id to edit',
        'label': 'The label of the API. (80 characters max)',
        'url': 'The root endpoint of the web Api: http://www.example.com/api.',
        'description': 'A short description of the API (400 characters max)',
        'tags': 'List of tags to help the search later. (400 characters max)'
    })
    @apis_ns.expect(patch_parser)
    def patch(self, id):
        args = self.patch_parser.parse_args()
        label = args.get('label')
        url = args.get('url')
        description = args.get('description')
        tags = args.get('tags')
        return JsonMethods.edit_api(id, label, url, description=description, tags=tags)

    @apis_ns.doc(description='Delete an API', params={
        'id': 'api id to delete'
    })
    def delete(self, id):
        return JsonMethods.delete_api(id)

endpoints_ns = Namespace('endpoints', 'Endpoints CRUD operations')
api.add_namespace(endpoints_ns)

@endpoints_ns.route('/')
class Endpoints(Resource):
    get_parser = api.parser()
    get_parser.add_argument('count', type=inputs.boolean, required=False)
    get_parser.add_argument('tags', type=str, required=False)
    get_parser.add_argument('page', type=int, required=False)
    get_parser.add_argument('api_id', type=int, required=False)
    @endpoints_ns.expect(get_parser)
    @endpoints_ns.doc(description="Get the count or a list of API items by query", params={
        'count': "A boolean. If True returns just the count of all APIs.",
        'page': "The requested page of API items (page 1 by default)",
        'tags': "Search APIs by tags",
        'api_id': "Use this id to get the corresponding API item endpoints list"
    })
    def get(self):
        args = self.get_parser.parse_args()
        count = args.get('count')
        page = args.get('page')
        tags = args.get('tags')
        api_id = args.get('api_id')
        if count:
            return JsonMethods.get_endpoints_count()
        return JsonMethods.get_endpoints(api_id=api_id, page=page, tags=tags)

    post_parser = api.parser()
    post_parser.add_argument('api_id', type=int, required=True)
    post_parser.add_argument('label', type=iv.str_validation(max=80), required=True)
    post_parser.add_argument('url', type=iv.url_validation('relative_endpoint'), required=True)
    post_parser.add_argument('description', type=iv.str_validation(max=400), required=False)
    post_parser.add_argument('tags', type=iv.str_validation(max=400), required=False)
    @endpoints_ns.doc(description='Add an endpoint', params={
        'api_id': 'The api id containing this endpoint',
        'label': 'The label of the endpoint. (80 characters max)',
        'url': 'The endpoint relative path. Example: /resource/subresource/endpoint',
        'description': 'A short description of the API. (400 characters max)',
        'tags': 'List of tags to help the search later. (400 characters max)'
    })
    @endpoints_ns.expect(post_parser)
    def post(self):
        args = self.post_parser.parse_args()
        api_id = args.get('api_id')
        label = args.get('label')
        url = args.get('url')
        description = args.get('description')
        tags = args.get('tags') if args.get('tags') else None
        return JsonMethods.add_endpoint(api_id, label, url, description=description, tags=tags)

@endpoints_ns.route('/<int:id>')
class EndpointItem(Resource):
    @endpoints_ns.doc(description="Get an Endpoint item by id", params={
        'id': "The id of the Endpoint"
    })
    def get(self, id):
        return JsonMethods.get_endpoint(id)

    patch_parser = api.parser()
    patch_parser.add_argument('label', type=iv.str_validation(max=80), required=False)
    patch_parser.add_argument('url', type=iv.url_validation('relative_endpoint'), required=False)
    patch_parser.add_argument('description', type=iv.str_validation(max=400), required=False)
    patch_parser.add_argument('tags', type=iv.str_validation(max=400), required=False)
    @endpoints_ns.doc(description='Edit an endpoint', params={
        'id': 'The endpoint id',
        'label': 'The label of the endpoint. (80 characters max)',
        'url': 'The endpoint relative path. Example: /resource/subresource/endpoint',
        'description': 'A short description of the API. (400 characters max)',
        'tags': 'List of tags to help the search later. (400 characters max)'
    })
    @endpoints_ns.expect(patch_parser)
    def patch(self, id):
        args = self.patch_parser.parse_args()
        label = args.get('label')
        url = args.get('url')
        description = args.get('description')
        tags = args.get('tags') if args.get('tags') else None
        return JsonMethods.edit_endpoint(id, label=label, url=url, description=description, tags=tags)

    @endpoints_ns.doc(description='Delete an endpoint', params={
        'id': 'api id to delete'
    })
    def delete(self, id):
        return JsonMethods.delete_endpoint(id)

fields_ns = Namespace('fields', 'Fields CRUD operations')
api.add_namespace(fields_ns)

@fields_ns.route('/')
class Fields(Resource):
    post_parser = api.parser()
    post_parser.add_argument('endpoint_id', type=int, required=True)
    post_parser.add_argument('label', type=iv.str_validation(max=80), required=True)
    post_parser.add_argument('field_type', type=str, required=True, choices=Globals.ACCEPTED_FIELD_TYPES)
    post_parser.add_argument('required', type=str, required=False, choices=Globals.ACCEPTED_FIELD_REQUIRED)
    post_parser.add_argument('default', type=iv.str_validation(max=200), required=False)
    post_parser.add_argument('description', type=iv.str_validation(max=400), required=False)
    @fields_ns.doc(description='Add a field to an endpoint', params={
        'endpoint_id': 'The endpoint id',
        'label': 'The label of the Field. (80 characters max)',
        'field_type': 'The field type. Must be in %s' % Globals.ACCEPTED_FIELD_TYPES,
        'required': 'is the field required? Must be in %s' % Globals.ACCEPTED_FIELD_REQUIRED,
        'default': 'The field default value. (200 characters max)',
        'description': 'The field description. (400 characters max)'
    })
    @fields_ns.expect(post_parser)
    def post(self):
        args = self.post_parser.parse_args()
        endpoint_id = args.get('endpoint_id')
        label = args.get('label')
        field_type = args.get('field_type')
        required = args.get('required')
        default = args.get('default')
        description = args.get('description')
        return JsonMethods.add_field(
            endpoint_id, label, field_type, required=required,
            default=default, description=description
        )

@fields_ns.route('/<int:id>')
class FieldItem(Resource):
    @fields_ns.doc(description="Get a Field item by id", params={
        'id': "The id of the Field"
    })
    def get(self, id):
        return JsonMethods.get_field(id)

    patch_parser = api.parser()
    patch_parser.add_argument('label', type=iv.str_validation(max=80), required=False)
    patch_parser.add_argument('field_type', type=str, required=False, choices=Globals.ACCEPTED_FIELD_TYPES)
    patch_parser.add_argument('required', type=str, required=False, choices=Globals.ACCEPTED_FIELD_REQUIRED)
    patch_parser.add_argument('default', type=iv.str_validation(max=200), required=False)
    patch_parser.add_argument('description', type=iv.str_validation(max=400), required=False)
    @fields_ns.doc(description='Edit a field', params={
        'id': 'The field id',
        'label': 'The label of the Field. (80 characters max)',
        'field_type': 'The field type. Must be in %s' % Globals.ACCEPTED_FIELD_TYPES,
        'required': 'is the field required? Must be in %s' % Globals.ACCEPTED_FIELD_REQUIRED,
        'default': 'The field default value. (200 characters max)',
        'description': 'The field description. (400 characters max)'
    })
    @fields_ns.expect(patch_parser)
    def patch(self, id):
        args = self.patch_parser.parse_args()
        label = args.get('label')
        field_type = args.get('field_type')
        required = args.get('required')
        default = args.get('default')
        description = args.get('description')
        return JsonMethods.edit_field(
            id, label=label, field_type=field_type, required=required,
            default=default, description=description
        )

    @fields_ns.doc(description='Delete an endpoint field', params={
        'id': 'the field id to delete'
    })
    def delete(self, id):
        return JsonMethods.delete_field(id)

class JsonMethods:
    @staticmethod
    def get_api(id):
        api = CRUD.getApi(id)
        if not api: return {}
        j = api_schema.dump(api)
        return j

    @staticmethod
    def get_apis(tags=None, page=None):
        if tags:
            apis = CRUD.getApis(tags=tags)
        else:
            if page:
                apis = CRUD.getApis(page=page)
            else:
                apis = CRUD.getApis(page=1)

        j = apis_schema.dump(apis)
        return j

    @staticmethod
    def get_apis_count():
        return {'count': ApiItem.query.count()}

    @staticmethod
    def delete_api(id):
        code = CRUD.deleteApi(id, commit=True)
        if code == 0:
            return {
                'status': 'error',
                'message': 'API #%d was not found. Maybe it was alredy deleted' % id,
                'id': id
            }
        elif code == -1:
            return {
                'status': 'error',
                'message': 'Oooops! Something went wrong while deleting API #%d' % id,
                'id': id
            }
        elif code > 0:
            return {
                'status': 'ok',
                'message': "API #%d was successfully deleted" % id,
                'id': id
            }

    @staticmethod
    def add_api(label, url, description=None, tags=None):
        new_id = CRUD.addApi(label, url, tags=tags, description=description, commit=True)
        if new_id:
            return {'status': 'ok', 'message': 'API %s was added' % label, 'id': new_id}
        else:
            return {
                'status': 'error',
                'message': 'Ooops! Something went wrong while adding API %s' % label
            }

    @staticmethod
    def edit_api(id, label, url, description=None, tags=None):
        code = CRUD.editApi(id, label=label, url=url, description=description, tags=tags, commit=True)
        if code == 0:
            return {
                'status': 'error',
                'message': 'API #%d was not found' % id,
                'id': id
            }
        elif code == -1:
            return {
                'status': 'error',
                'message': 'Oooops! Something went wrong while editing API #%d' % id,
                'id': id
            }
        elif code > 0:
            return {
                'status': 'ok',
                'message': 'API #%d was successfully edited' % id,
                'id': id
            }

    @staticmethod
    def get_endpoint(id):
        endpoint = CRUD.getEndpoint(id)
        j = endpoint_schema.dump(endpoint)
        return j

    @staticmethod
    def get_endpoints(api_id=None, page=None, tags=None):
        if api_id:
            api = CRUD.getApi(api_id)
            endpoints = api.endpoints
        elif tags:
            endpoints = CRUD.getEndpoints(tags=tags)
        else:
            if page:
                endpoints = CRUD.getEndpoints(page=page)
            else:
                endpoints = CRUD.getEndpoints(page=1)

        j = endpoints_schema.dump(endpoints)
        return j

    @staticmethod
    def get_endpoints_count():
        return {'count': Endpoint.query.count()}

    @staticmethod
    def add_endpoint(api_id, label, url, description=None, tags=None):
        new_id = CRUD.addEndpoint(
            api_id, label, url, description=description,
            tags=tags, commit=True
        )
        if new_id:
            return {'status': 'ok', 'message': 'Endpoint %s was added' % label, 'id': new_id}
        else:
            return {
                'status': 'error',
                'message': 'Ooops! Something went wrong while adding Endpoint %s' % label
            }

    @staticmethod
    def delete_endpoint(id):
        code = CRUD.deleteEndpoint(id, commit=True)
        if code == 0:
            return {
                'status': 'error',
                'message': 'Endpoint #%d was not found. Maybe it was alredy deleted' % id,
                'id': id
            }
        elif code == -1:
            return {
                'status': 'error',
                'message': 'Oooops! Something went wrong while deleting Endpoint #%d' % id,
                'id': id
            }
        elif code > 0:
            return {
                'status': 'ok',
                'message': 'endpoint #%d was successfully deleted' % id,
                'id': id
            }

    @staticmethod
    def edit_endpoint(id, label=None, url=None, description=None, tags=None):
        code = CRUD.editEndpoint(id, label=label, url=url, description=description, tags=tags, commit=True)
        if code == 0:
            return {
                'status': 'error',
                'message': 'Endpoint #%d was not found' % id,
                'id': id
            }
        elif code == -1:
            return {
                'status': 'error',
                'message': 'Oooops! Something went wrong while editing Endpoint #%d' % id,
                'id': id
            }
        elif code > 0:
            return {
                'status': 'ok',
                'message': 'Endpoint #%d was successfully edited' % id,
                'id': id
            }

    @staticmethod
    def get_field(id):
        field = CRUD.getField(id)
        if not field: return {}
        j = field_schema.dump(field)
        return j

    @staticmethod
    def add_field(endpoint_id, label, field_type, required='no', default=None, description=None):
        if field_type not in Globals.ACCEPTED_FIELD_TYPES:
            return {
                'status': 'error',
                'message': '%s is not accepted as a field type. Must be one of these: %s' % (
                    field_type, Globals.ACCEPTED_FIELD_TYPES
                )
            }

        if required not in Globals.ACCEPTED_FIELD_REQUIRED:
            return {
                'status': 'error',
                'message': '%s is not accepted as a required parameter. Must be one of these: %s' % (
                    required, Globals.ACCEPTED_FIELD_REQUIRED
                )
            }

        required = True if required == 'yes' else False

        new_id = CRUD.addEndpointField(
            endpoint_id, label, field_type, description=description,
            default=default, required=required, commit=True
        )
        if new_id:
            return {
                'status': 'ok',
                'message': 'Field %s was added' % label,
                'id': new_id
            }
        else:
            return {
                'status': 'error',
                'message': 'Ooops! Something went wrong while adding Field %s' % label
            }

    @staticmethod
    def delete_field(field_id):
        code = CRUD.deleteField(field_id, commit=True)
        if code == 0:
            return {
                'status': 'error',
                'message': 'Field #%d was not found. Maybe it was alredy deleted' % field_id,
                'id': field_id
            }
        elif code == -1:
            return {
                'status': 'error',
                'message': 'Oooops! Something went wrong while deleting Field #%d' % field_id,
                'id': field_id
            }
        elif code > 0:
            return {
                'status': 'ok',
                'message': 'Field #%d was successfully deleted' % field_id,
                'id': field_id
            }

    @staticmethod
    def edit_field(field_id, label=None, field_type=None, required=None, default=None, description=None):
        if field_type and field_type not in Globals.ACCEPTED_FIELD_TYPES:
            return {
                'status': 'error',
                'message': '%s is not accepted as a field type. Must be one of these: %s' % (
                    field_type, Globals.ACCEPTED_FIELD_TYPES
                )
            }

        if required and required not in Globals.ACCEPTED_FIELD_REQUIRED:
            return {
                'status': 'error',
                'message': '%s is not accepted as a required parameter. Must be one of these: %s' % (
                    required, Globals.ACCEPTED_FIELD_REQUIRED
                )
            }

        required = True if required == 'yes' else False

        code = CRUD.editField(
            field_id, label=label, type_field=field_type,
            required=required, default=default,
            description=description, commit=True
        )
        if code == 0:
            return {
                'status': 'error',
                'message': 'Field #%d was not found' % field_id,
                'id': field_id
            }
        elif code == -1:
            return {
                'status': 'error',
                'message': 'Oooops! Something went wrong while editing Field #%d' % field_id,
                'id': field_id
            }
        elif code>0:
            return {
                'status': 'ok',
                'message': 'Endpoint #%d was successfully edited' % field_id,
                'id': field_id
            }
