from sqlalchemy.exc import IntegrityError

from config import Globals
from models import db, Tag, ApiItem, Endpoint, Field

class CRUD:
    @staticmethod
    def addTag(text, commit=False):
        text = text.lower().strip()
        existing_tag = Tag.query.filter_by(text=text).first()
        if existing_tag:
            return existing_tag

        tag = Tag(text=text)
        db.session.add(tag)
        try:
            db.session.flush()
            if commit:
                db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None

        db.session.refresh(tag)
        return tag

    @staticmethod
    def addTags(tags, commit=False):
        metatags = []
        tags_list = tags.strip().split()
        for tag_text in tags_list:
            metatags.append(CRUD.addTag(tag_text, commit=commit))

        return metatags

    @staticmethod
    def addApi(label, url, description='', tags=None, commit=False):
        metatags = CRUD.addTags(tags, commit) if tags else []
        api = ApiItem(label=label, url=url, description=description, tags=metatags)
        db.session.add(api)
        try:
            db.session.flush()
            if commit:
                db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None

        db.session.refresh(api)
        return api.id

    @staticmethod
    def getApi(id):
        api = ApiItem.query.filter_by(id=id).first()
        return api

    @staticmethod
    def getApis(tags=None, page=None):
        apis = []
        query = ApiItem.query
        if tags:
            tags = tags.strip().split()
            tags = [t.lower() for t in tags]
            apis.extend(query.filter(ApiItem.label.ilike(' '.join(tags))).all())
            for tag_text in tags:
                # search by tags and labels
                apis.extend(query.filter(ApiItem.tags.any(Tag.text == tag_text)).all())
                apis.extend(query.filter(ApiItem.label.ilike(tag_text)).all())

            deduplicated = list(set(apis))
            apis_relevance = []
            for api in deduplicated:
                api_tags = [t.text for t in api.tags]
                if api.label.lower() in ' '.join(tags):
                    relevance = float('inf')
                else:
                    relevance = len([t for t in api_tags if t in tags])
                apis_relevance.append({'api': api, 'relevance': relevance})

            apis_relevance = sorted(apis_relevance, key=lambda x: -x['relevance'])
            sorted_apis = [a['api'] for a in apis_relevance]
            return sorted_apis[:Globals.ITEM_PER_PAGE]

        if page:
            apis = query.paginate(page, Globals.ITEM_PER_PAGE).items
            return apis

        apis = query.all()
        return apis

    @staticmethod
    def deleteApi(id, commit=False):
        api = CRUD.getApi(id)
        if api:
            try:
                code = api.id
                db.session.delete(api)
                db.session.flush()
                if commit:
                    db.session.commit()
            except IntegrityError:
                code = - 1
                db.session.rollback()
        else:
            code = 0
        return code

    @staticmethod
    def editApi(id, label=None, url=None, description=None, tags=None, commit=False):
        api = CRUD.getApi(id)
        if api:
            try:
                code = api.id
                if label is not None: api.label = label
                if url is not None: api.url = url
                if description is not None: api.description = description
                if tags is not None: api.tags = CRUD.addTags(tags, commit)

                db.session.add(api)
                db.session.flush()
                if commit:
                    db.session.commit()
            except IntegrityError:
                code = - 1
                db.session.rollback()
        else:
            code = 0
        return code

    @staticmethod
    def addEndpoint(api_id, label, url, description='', tags=None, commit=False):
        metatags = CRUD.addTags(tags, commit) if tags else []
        endpoint = Endpoint(api_item_id=api_id, label=label, url=url, description=description, tags=metatags)
        db.session.add(endpoint)
        try:
            db.session.flush()
            if commit:
                db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None

        db.session.refresh(endpoint)
        return endpoint.id

    @staticmethod
    def getEndpoint(id):
        endpoint = Endpoint.query.filter_by(id=id).first()
        return endpoint

    @staticmethod
    def getEndpoints(tags=None, page=None):
        endpoints = []
        query = Endpoint.query
        if tags:
            tags = tags.strip().split()
            tags = [t.lower() for t in tags]
            endpoints.extend(query.filter(Endpoint.label.ilike(' '.join(tags))).all())
            for tag_text in tags:
                # search by tags and label
                endpoints.extend(query.filter(Endpoint.tags.any(Tag.text == tag_text)).all())
                endpoints.extend(query.filter(Endpoint.label.ilike(tag_text)).all())

                deduplicated = list(set(endpoints))
                endpoints_relevance = []
                for endpoint in deduplicated:
                    endpoint_tags = [t.text for t in endpoint.tags]
                    if endpoint.label.lower() in ' '.join(tags):
                        relevance = float('inf')
                    else:
                        relevance = len([t for t in endpoint_tags if t in tags])
                    endpoints_relevance.append({'endpoint': endpoint, 'relevance': relevance})

                endpoints_relevance = sorted(endpoints_relevance, key=lambda x: -x['relevance'])
                sorted_endpoints = [a['endpoint'] for a in endpoints_relevance]
                return sorted_endpoints

        if page:
            endpoints = query.paginate(page, Globals.ITEM_PER_PAGE).items
            return endpoints

        endpoints = query.all()
        return endpoints

    @staticmethod
    def deleteEndpoint(id, commit=False):
        endpoint = CRUD.getEndpoint(id)
        if endpoint:
            try:
                code = endpoint.id
                db.session.delete(endpoint)
                db.session.flush()
                if commit:
                    db.session.commit()
            except IntegrityError:
                code = - 1
                db.session.rollback()
        else:
            code = 0
        return code

    @staticmethod
    def editEndpoint(id, label=None, url=None, description=None, tags=None, commit=False):
        endpoint = CRUD.getEndpoint(id)
        if endpoint:
            try:
                code = endpoint.id
                if label is not None: endpoint.label = label
                if url is not None: endpoint.url = url
                if description is not None: endpoint.description = description
                if tags is not None: endpoint.tags = CRUD.addTags(tags, commit)

                db.session.add(endpoint)
                db.session.flush()
                if commit:
                    db.session.commit()
            except IntegrityError:
                code = - 1
                db.session.rollback()
        else:
            code = 0
        return code

    @staticmethod
    def getEndpointFields(endpoint_id):
        fields = Field.query.filter_by(endpoint_id=endpoint_id).all()
        return fields

    @staticmethod
    def getField(id):
        field = Field.query.filter_by(id=id).first()
        return field

    @staticmethod
    def addEndpointField(endpoint_id, label, type_field, description='', default='', required=False, commit=False):
        field = Field(
            endpoint_id=endpoint_id, label=label, type=type_field,
            description=description, default=default, required=required
        )
        try:
            db.session.add(field)
            db.session.flush()
            if commit:
                db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None

        db.session.refresh(field)
        return field.id

    @staticmethod
    def editField(field_id, label=None, type_field=None, description=None, default=None, required=None, commit=False):
        field = CRUD.getField(field_id)
        if field:
            try:
                code = field.id
                if label is not None: field.label = label
                if type_field is not None:
                    if type_field != field.type: field.default = ''
                    field.type = type_field
                if description is not None: field.description = description
                if default is not None: field.default = default
                if required is not None: field.required = required

                db.session.add(field)
                db.session.flush()
                if commit:
                    db.session.commit()
            except IntegrityError:
                code = - 1
                db.session.rollback()
        else:
            code = 0
        return code

    @staticmethod
    def deleteField(id, commit=False):
        field = CRUD.getField(id)
        if field:
            try:
                code = field.id
                db.session.delete(field)
                db.session.flush()
                if commit:
                    db.session.commit()
            except IntegrityError:
                code = - 1
                db.session.rollback()
        else:
            code = 0
        return code
