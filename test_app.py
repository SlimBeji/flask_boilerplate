#pytest -W ignore -s
import pytest, random

from app import app as flask_app
from models import Tag
from crud import CRUD, db
from utils import generate_random_string

print('\n=> Starting testing')
@pytest.fixture(scope="session")
def app():
    flask_app.app_context().push()
    return flask_app

#============HTTP testing=================
@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

def test_index_page(client):
    print('\n=> Testing the index page returns a 200 status code')
    response = client.get('/')
    assert response.status_code == 200

#============CRUD testing=================
# Mocking db.sessions.commit() to avoid commiting
# test objects by mistake
@pytest.fixture(scope="function")
def mock_crud(mocker):
    return mocker.patch(
        "crud.db.session.commit",
        return_value=True
    )

@pytest.fixture(scope="function")
def context_tags(mock_crud):
    tags_str = [generate_random_string() for _ in range(2)]
    metatags = CRUD.addTags(tags_str, commit=False)
    context = {'tags': metatags, 'tags_str': tags_str}
    return context

def test_adding_multiple_tags(mock_crud, context_tags):
    print('\n=> Testing adding multiple tags to the database')
    assert len(context_tags.get('tags')) > 1

@pytest.fixture(scope="function")
def context_api(mock_crud, context_tags):
    context = context_tags
    label = generate_random_string()
    url = generate_random_string()
    description = ' '.join([generate_random_string() for _ in range(5)])
    tags = context.get('tags_str')
    api_id = CRUD.addApi(label, url, description=description, tags=tags, commit=False)
    context['api_id'] = api_id
    return context

def test_adding_api(mock_crud, context_api):
    print('\n=> Testing adding api to the database')
    api_id = context_api.get('api_id')
    assert api_id
    api = CRUD.getApi(api_id)
    assert api

def test_edit_api_by_id(mock_crud, context_api):
    print('\n=> Testing editing api by id')
    id = context_api.get('api_id')
    label = generate_random_string()
    url = generate_random_string()
    description = ' '.join([generate_random_string() for _ in range(5)])
    tags = [generate_random_string() for _ in range(5)]
    code = CRUD.editApi(
        id,
        name=label,
        url=url,
        description=description,
        tags=tags
    )
    assert code>0
    api = CRUD.getApi(id)
    assert api.label == label
    assert api.url == url
    assert api.description == description
    assert set(tags) == set([t.text for t in api.tags])

def test_filter_apis_by_tags(mock_crud, context_api):
    print('\n=> Testing filtering apis by tags')
    apis = CRUD.getApis(context_api.get('tags_str'))
    assert apis

@pytest.fixture(scope="function")
def context_endpoint(mock_crud, context_api):
    context = context_api
    api_id = context.get('api_id')
    label = generate_random_string()
    url = generate_random_string()
    description = ' '.join([generate_random_string() for _ in range(5)])
    tags = context.get('tags_str')
    id = CRUD.addEndpoint(
        api_id,
        label,
        url,
        description,
        tags=tags,
        commit=False
    )
    context['endpoint_id'] = id
    return context

def test_adding_endpoint(mock_crud, context_endpoint):
    print('\n=> Testing adding endpoint to the database')
    assert context_endpoint.get('endpoint_id')

def test_edit_endpoint_by_id(mock_crud, context_endpoint):
    print('\n=> Testing editing endpoint by id')
    endpoint_id = context_endpoint.get('endpoint_id')
    label = generate_random_string()
    url = generate_random_string()
    description = ' '.join([generate_random_string() for _ in range(5)])
    tags = [generate_random_string() for _ in range(5)]
    code = CRUD.editEndpoint(
        endpoint_id,
        name=label,
        url=url,
        description=description,
        tags=tags
    )
    assert code>0
    endpoint = CRUD.getEndpoint(endpoint_id)
    assert endpoint.label == label
    assert endpoint.url == url
    assert endpoint.description == description
    assert set(tags) == set([t.text for t in endpoint.tags])

def test_delete_endpoint_by_id(mock_crud, context_endpoint):
    print('\n=> Testing deleting endpoint by id')
    code = CRUD.deleteEndpoint(context_endpoint.get('endpoint_id'))
    assert code>0

@pytest.fixture(scope="function")
def context_field(mock_crud, context_endpoint):
    context = context_endpoint
    endpoint_id = context.get('endpoint_id')
    name = generate_random_string()
    type_field = generate_random_string()
    description = ' '.join([generate_random_string() for _ in range(5)])
    default = generate_random_string()
    required = random.choice([True, False])
    id = CRUD.addEndpointField(
        endpoint_id,
        name,
        type_field,
        description=description,
        default=default,
        required=required,
        commit=False
    )
    context['field_id'] = id
    return context

def test_adding_field(mock_crud, context_field):
    print('\n=> Testing adding a field to an endpoint')
    assert context_field.get('field_id')

def test_edit_field_by_id(mock_crud, context_field):
    print('\n=> Testing editing field by id')
    field_id = context_field.get('field_id')
    name = generate_random_string()
    type_field = generate_random_string()
    description = ' '.join([generate_random_string() for _ in range(5)])
    default = generate_random_string()
    required = random.choice([True, False])
    code = CRUD.editField(
        field_id,
        name=name,
        type_field=type_field,
        description=description,
        default=default,
        required=required,
        commit=False
    )
    assert code>0
    field = CRUD.getField(field_id)
    assert field.name == name
    assert field.type == type_field
    assert field.description == description
    assert field.default == default
    assert field.required == required

def test_deleting_field(mock_crud, context_field):
    print('\n=> Testing deleting field by id')
    code = CRUD.deleteField(context_field.get('field_id'))
    assert code>0

def test_cascade_delete_api_by_id(mock_crud, context_field):
    print('\n=> Testing cascade deleting api by id')
    api_id = context_field.get('api_id')
    endpoint_id = context_field.get('endpoint_id')
    field_id = context_field.get('field_id')

    code = CRUD.deleteApi(api_id)
    assert code>0
    existing_endpoint_id = CRUD.getEndpoint(endpoint_id)
    assert existing_endpoint_id is None
    existing_field = CRUD.getField(field_id)
    assert existing_field is None
