from urllib.parse import urlparse
import re
import validators
from validators.utils import ValidationFailure

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, URL

from config import Globals

class ApiInputValidation:
    @staticmethod
    def str_validation(min=1, max=None):
        def validate(value):
            if isinstance(value, str):
                if min and len(value) < min:
                    raise ValueError("Must be %d characters at least" % min)
                if max and len(value) > max:
                    raise ValueError("Must be %d characters at most" % max)
                return value
            else:
                raise ValueError("%s is not of a type string" % value)

        return validate

    @staticmethod
    def url_validation(type=None):
        def validate(value):
            if type=='domain':
                if validators.domain(value) is True:
                    return value
                else:
                    raise ValueError("%s is not a valid domain name" % value)
            elif type == 'endpoint':
                if validators.url(value) is True:
                    parsed = urlparse(value)
                    if parsed.query or parsed.fragment:
                        raise ValueError("%s is not a valid endpoint. It contains query params or framents" % value)
                    else:
                        return value
                else:
                    raise ValueError("%s is not a valid endpoint" % value)
            elif type=='relative_endpoint':
                r = r'(^\/([a-zA-Z0-9#\_\-\.]+\/?)+$)'
                match = re.findall(r, value)
                if match:
                    return value.rstrip('/')
                else:
                    raise ValueError("%s is not a valid relative endpoint." % value)
            else:
                if validators.url(value) is True:
                    return value
                else:
                    raise ValueError("%s is not a valid url" % value)
        return validate

class AddApiForm(FlaskForm):
    label = StringField('Label', validators=[DataRequired(), Length(max=80)])
    url = StringField('Url', validators=[DataRequired(), URL()])
    description = TextAreaField('Description', validators=[Length(max=400)])
    tags = StringField('Tags', validators=[Length(max=400)])

class EditApiForm(AddApiForm):
    pass

class AddEndpointForm(FlaskForm):
    label = StringField('Label', validators=[DataRequired(), Length(max=80)])
    url = StringField('Url', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=400)])
    tags = StringField('Tags', validators=[Length(max=400)])

    def validate_url(self, field):
        print(field.data)
        ApiInputValidation.url_validation('relative_endpoint')(field.data)

class EditEndpointForm(AddEndpointForm):
    pass

class AddFieldForm(FlaskForm):
    label = StringField('Label', validators=[DataRequired(), Length(max=80)])
    type = SelectField('Type', validators=[DataRequired()], choices=Globals.ACCEPTED_FIELD_TYPES)
    required = SelectField('Required', validators=[DataRequired()], choices=Globals.ACCEPTED_FIELD_REQUIRED)
    default = StringField('Default', validators=[Length(max=200)])
    description = TextAreaField('Description', validators=[Length(max=400)])

class EditFieldForm(AddFieldForm):
    pass
