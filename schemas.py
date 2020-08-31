from flask_marshmallow import Marshmallow
from flask_marshmallow.fields import fields

from models import ApiItem, Endpoint, Field, Tag
from config import Globals

ma = Marshmallow()

class TagSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tag

tag_schema = TagSchema()
tags_schema = TagSchema(many=True)

class MyBoolean(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        if value is True:
            return "yes"
        return "no"

    def _deserialize(self, value, attr, data, **kwargs):
        if value not in Globals.ACCEPTED_FIELD_REQUIRED:
            raise ValueError('Cannot deserialize')
        if value=='yes': return True
        return False

class FieldSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Field

    endpoint_id = ma.auto_field()
    required = MyBoolean()

field_schema = FieldSchema()
fields_schema = FieldSchema(many=True)

class ApiSchemaRaw(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ApiItem

    tags = fields.List(fields.Pluck(TagSchema, "text"), many=True)

class EndpointSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Endpoint

    tags = fields.List(fields.Pluck(TagSchema, "text"), many=True)
    fields_list = fields.List(fields.Nested(FieldSchema, exclude=['endpoint_id']), attribute="fields")
    api_item = fields.Nested(ApiSchemaRaw)

endpoint_schema = EndpointSchema()
endpoints_schema = EndpointSchema(many=True)

class ApiSchema(ApiSchemaRaw):
    endpoints = fields.List(fields.Nested(EndpointSchema))

api_schema = ApiSchema()
apis_schema = ApiSchema(many=True)
