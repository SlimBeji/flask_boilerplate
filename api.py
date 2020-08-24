from flask_restx import Api, Namespace, Resource, reqparse

from crud import CRUD
from extensions import csrf
from config import Globals
from utils import from_sql_to_dict

api_ns = Namespace('api', 'CRUD operations API')

@api_ns.route('/apis/get_api/<int:id>')
class GetApi(Resource):
    def get(self, id):
        api = CRUD.getApi(id)
        j = from_sql_to_dict(api)
        return j

@api_ns.route('/apis/add_api')
class AddApi(Resource):
    postParser = reqparse.RequestParser()
    postParser.add_argument('name', type=str, required=True)
    postParser.add_argument('url', type=str, required=True)
    postParser.add_argument('description', type=str, required=False)
    postParser.add_argument('tags', type=str, required=False)

    @api_ns.expect(postParser)
    @api_ns.doc(description='Add an API', params={
        'name': 'The name/label of the API. (80 characters max)',
        'url': 'The url of the web App. (200 characters max)',
        'description': 'A short description of the API (400 characters max)',
        'tags': 'List of tags to help the search later. (400 characters max)'
    })

    def post(self):
        args = self.postParser.parse_args()
        name = args.get('name')
        url = args.get('url')
        description = args.get('description')
        tags = args.get('tags').strip().split()

        new_id = CRUD.addApi(name, url, tags=tags, description=description, commit=True)
        if new_id:
            return {'status':'ok', 'message': 'API %s was added' % name, 'id': new_id}
        else:
            return {
                'status': 'error',
                'message': 'Ooops! Something went wrong while adding API %s' % name
            }

@api_ns.route('/apis/delete/<int:id>')
class DeleteApi(Resource):
    @api_ns.doc(description='Delete an API', params={
        'id': 'api id to delete'
    })
    def post(self, id):
        code = CRUD.deleteApi(id, commit=True)
        if code == 0:
            return {
                'status': 'error',
                'message': 'API #%d was not found. Maybe it was alredy deleted' % id,
                'id':id
            }
        elif code == -1:
            return {
                'status': 'error',
                'message': 'Oooops! Something went wrong while deleting API #%d' % id,
                'id':id
            }
        elif code > 0:
            return {
                'status': 'ok',
                'message': "API #%d was successfully deleted" % id,
                'id':id
            }

@api_ns.route('/apis/edit/<int:id>')
class EditApi(Resource):
    postParser = reqparse.RequestParser()
    postParser.add_argument('name', type=str, required=True)
    postParser.add_argument('url', type=str, required=True)
    postParser.add_argument('description', type=str, required=False)
    postParser.add_argument('tags', type=str, required=False)
    @api_ns.expect(postParser)
    @api_ns.doc(description='Edit an API', params={
        'id': 'The api id to edit',
        'name': 'The name/label of the API. (80 characters max)',
        'url': 'The url of the web App. (200 characters max)',
        'description':'A short description of the API (400 characters max)',
        'tags':'List of tags to help the search later. Example: weather free (400 characters max)'
    })
    def post(self, id):
        args = self.postParser.parse_args()
        name = args.get('name')
        url = args.get('url')
        description = args.get('description')
        tags = args.get('tags').strip().split() if args.get('tags') else None

        code = CRUD.editApi(id, name=name, url=url, description=description, tags=tags, commit=True)
        if code == 0:
            return {
                'status':'error',
                'message': 'API #%d was not found' % id,
                'id':id
            }
        elif code == -1:
            return {
                'status': 'error',
                'message': 'Oooops! Something went wrong while editing API #%d' % id,
                'id': id
            }
        elif code>0:
            return {
                'status': 'ok',
                'message': 'API #%d was successfully edited' % id,
                'id': id
            }

@api_ns.route('/endpoints/add')
class AddEndpoint(Resource):
    postParser = reqparse.RequestParser()
    postParser.add_argument('api', type=str, required=True)
    postParser.add_argument('name', type=str, required=True)
    postParser.add_argument('url', type=str, required=True)
    postParser.add_argument('description', type=str, required=False)
    postParser.add_argument('tags', type=str, required=False)

    @api_ns.expect(postParser)
    @api_ns.doc(description='Add an endpoint', params={
        'api': 'The api id containing this endpoint',
        'name': 'The label of the endpoint. By default the same as the url if not specified (80 characters max)',
        'url': 'The url of the endpoint. (200 characters max)',
        'description': 'A short description of the API. (400 characters max)',
        'tags': 'List of tags to help the search later. (400 characters max)'
    })
    def post(self):
        args = self.postParser.parse_args()
        api_id = args.get('api')
        name = args.get('name')
        url = args.get('url')
        description = args.get('description')
        tags = args.get('tags').strip().split() if args.get('tags') else None

        new_id = CRUD.addEndpoint(
            api_id, name, url, description=description,
            tags=tags, commit=True
        )
        if new_id:
            return {'status':'ok', 'message':'Endpoint %s was added' % name, 'id':new_id}
        else:
            return {
                'status': 'error',
                'message': 'Ooops! Something went wrong while adding Endpoint %s' % name
            }

@api_ns.route('/endpoints/<int:id>/delete')
class DeleteEndpoint(Resource):
    @api_ns.doc(description='Delete an endpoint', params={
        'id': 'api id to delete'
    })
    def post(self, id):
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
        elif code>0:
            return {
                'status': 'ok',
                'message': 'endpoint #%d was successfully deleted' % id,
                'id': id
            }

@api_ns.route('/endpoints/<int:id>/edit')
class EditEndpoint(Resource):
    postParser = reqparse.RequestParser()
    postParser.add_argument('name', type=str, required=True)
    postParser.add_argument('url', type=str, required=True)
    postParser.add_argument('description', type=str, required=False)
    postParser.add_argument('tags', type=str, required=False)
    @api_ns.expect(postParser)
    @api_ns.doc(description='Edit an endpoint',  params={
        'id': 'The endpoint id',
        'name': 'The label of the endpoint. By default the same as the url if not specified (80 characters max)',
        'url': 'The url of the endpoint (200 characters max)',
        'description': 'A short description of the endpoint. (400 characters max)',
        'tags': 'List of tags to help the search later. (400 characters max)'
    })
    def post(self, id):
        args = self.postParser.parse_args()
        name = args.get('name')
        url = args.get('url')
        description = args.get('description')
        tags = args.get('tags').strip().split() if args.get('tags') else None

        code = CRUD.editEndpoint(id, name=name, url=url, description=description, tags=tags, commit=True)
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
        elif code>0:
            return {
                'status': 'ok',
                'message': 'Endpoint #%d was successfully edited' % id,
                'id': id
            }

@api_ns.route('/endpoints/<int:endpoint_id>/add_field')
class AddFieldEndpoint(Resource):
    postParser = reqparse.RequestParser()
    postParser.add_argument('field_name', type=str, required=True)
    postParser.add_argument('field_type', type=str, required=True)
    postParser.add_argument('field_required', type=str, required=False)
    postParser.add_argument('field_default', type=str, required=False)
    postParser.add_argument('field_description', type=str, required=False)

    @api_ns.expect(postParser)
    @api_ns.doc(description='Add a field to an endpoint', params={
        'endpoint_id': 'The endpoint id',
        'field_name': 'The label of the Field. (80 characters max)',
        'field_type': 'The field type. Must be in %s' % Globals.ACCEPTED_FIELD_TYPES,
        'field_required': 'is the field required? Must be in %s' % Globals.ACCEPTED_FIELD_REQUIRED,
        'field_default': 'The field default value. (200 characters max)',
        'field_description': 'The field description. (400 characters max)'
    })
    def post(self, endpoint_id):
        args = self.postParser.parse_args()
        field_name = args.get('field_name')
        field_type = args.get('field_type')
        field_required = args.get('field_required')
        field_default = args.get('field_default')
        field_description = args.get('field_description')

        if field_type not in Globals.ACCEPTED_FIELD_TYPES:
            return {
                'status': 'error',
                'message': '%s is not accepted as a field type. Must be one of these: %s' % (
                    field_type, Globals.ACCEPTED_FIELD_TYPES
                )
            }

        if field_required not in Globals.ACCEPTED_FIELD_REQUIRED:
            return {
                'status': 'error',
                'message': '%s is not accepted as a field type. Must be one of these: %s' % (
                    field_type, Globals.ACCEPTED_FIELD_REQUIRED
                )
            }

        field_required = True if field_required == 'yes' else False

        new_id = CRUD.addEndpointField(
            endpoint_id,
            field_name,
            field_type,
            description=field_description,
            default=field_default,
            required=field_required,
            commit=True
        )
        if new_id:
            return {
                'status': 'ok',
                'message': 'Field %s was added' % field_name,
                'id': new_id
            }
        else:
            return {
                'status': 'error',
                'message': 'Ooops! Something went wrong while adding Field %s' % field_name
            }

@api_ns.route('/endpoints/<int:endpoint_id>/delete/<int:field_id>')
class DeleteField(Resource):
    @api_ns.doc(description='Delete a field from an endpoint', params={
        'endpoint_id': 'the endpoint id',
        'field_id': 'the field id to delete'
    })
    def post(self, endpoint_id, field_id):
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
        elif code>0:
            return {
                'status': 'ok',
                'message': 'Field #%d was successfully deleted' % field_id,
                'id': field_id
            }

@api_ns.route('/endpoints/<int:endpoint_id>/edit/<int:field_id>')
class editFieldRoute(Resource):
    postParser = reqparse.RequestParser()
    postParser.add_argument('field_name', type=str, required=True)
    postParser.add_argument('field_type', type=str, required=True)
    postParser.add_argument('field_required', type=str, required=False)
    postParser.add_argument('field_default', type=str, required=False)
    postParser.add_argument('field_description', type=str, required=False)

    @api_ns.expect(postParser)
    @api_ns.doc(description='Edit an endpoint field', params={
        'endpoint_id':'The endpoint id',
        'field_id': 'The field id',
        'field_name': 'The label of the Field. (200 characters max)',
        'field_type': 'The field type. Must be in %s' % Globals.ACCEPTED_FIELD_TYPES,
        'field_required': 'is the field required? Must be in %s' % Globals.ACCEPTED_FIELD_REQUIRED,
        'field_default': 'The field default value. (200 characters max)',
        'field_description': 'The field description. (400 characters max)'
    })
    def post(self, endpoint_id, field_id):
        args = self.postParser.parse_args()
        field_name = args.get('field_name')
        field_type = args.get('field_type')
        field_required = args.get('field_required')
        field_default = args.get('field_default')
        field_description = args.get('field_description')

        if field_type not in Globals.ACCEPTED_FIELD_TYPES:
            return {
                'status': 'error',
                'message': '%s is not accepted as a field type. Must be one of these: %s' % (
                    field_type, Globals.ACCEPTED_FIELD_TYPES
                )
            }

        if field_required not in Globals.ACCEPTED_FIELD_REQUIRED:
            return {
                'status': 'error',
                'message': '%s is not accepted as a field type. Must be one of these: %s' % (
                    field_type, Globals.ACCEPTED_FIELD_REQUIRED
                )
            }

        field_required = True if field_required == 'yes' else False

        code = CRUD.editField(
            field_id,
            name=field_name,
            type_field=field_type,
            required=field_required,
            default=field_default,
            description=field_description,
            commit=True
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

api = Api(
    title='CRUD API',
    version='1.0',
    description='API for CRUD operations',
    prefix='/api',
    doc='/swagger',
    decorators=[csrf.exempt]
)

api.add_namespace(api_ns)
