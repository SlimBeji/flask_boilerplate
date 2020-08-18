from datetime import datetime
from flask_sqlalchemy import  SQLAlchemy
from flask_security import SQLAlchemyUserDatastore, UserMixin, RoleMixin, Security

db = SQLAlchemy(session_options={'autocommit': False})

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

api_item_tag_table = db.Table(
    'api_item_tag',
    db.Column('api_item_id', db.Integer, db.ForeignKey('api_item.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

endpoint_tag_table = db.Table(
    'endpoint_tag',
    db.Column('endpoint_id', db.Integer, db.ForeignKey('endpoint.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime(), default=datetime.now())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email

class ApiItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(400), nullable=True)
    url = db.Column(db.String(200), nullable=False)
    endpoints = db.relationship('Endpoint', backref='api_item', lazy=True, cascade="all, delete-orphan")
    tags = db.relationship(
        'Tag', secondary=api_item_tag_table, lazy=True,
        backref=db.backref('api_items', lazy=True)
    )

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(80), nullable=False, unique=True)

class Endpoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_item_id = db.Column(db.Integer, db.ForeignKey('api_item.id'), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    label = db.Column(db.String(80), nullable=True)
    description = db.Column(db.String(400), nullable=True)
    fields = db.relationship(
        'Field', backref=db.backref('endpoints', lazy=True),
        lazy=True, cascade="all, delete-orphan"
    )
    tags = db.relationship(
        'Tag', secondary=endpoint_tag_table, lazy=True,
        backref=db.backref('endpoints', lazy=True)
    )

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('endpoint.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(400), nullable=True)
    default = db.Column(db.String(200), nullable=True)
    required = db.Column(db.Boolean, default=False)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()
