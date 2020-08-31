from urllib.parse import urlparse
import json, re, string, random
from urllib.parse import urlencode
from urllib import request

def from_sql_to_dict(obj):
    return {
        col.name: getattr(obj, col.name) for col in obj.__table__.columns
    }

def paginate(l, per_page, page, sort_expression=None):
    if sort_expression:
        l = sorted(l, key=sort_expression)
    slices = [l[i:i+per_page] for i in range(0, len(l), per_page)]
    sub_list = slices[page-1]
    return sub_list

def list_obj_stringify(params):
    list_str = params[0]
    attribute = params[1]
    list_str = [getattr(t, attribute) for t in list_str]
    return ' '.join(list_str)

def flatten_json(nested_json, exclude=None):
    """Flatten json object with nested keys into a single level.
    use "exclude" argument to exclude  keys"""
    out = {}

    def flatten(x, name='', exclude=exclude):
        if exclude is None: exclude = ['']
        if type(x) is dict:
            for a in x:
                if a not in exclude: flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(nested_json)
    return out

def get_json_response(current_app, view_name, *args, **kwargs):
    '''Calls internal view method, parses json, and returns python dict.'''
    view = current_app.view_functions[view_name]
    with current_app.request_context():
        res = view(*args, **kwargs)
    js = json.loads(res.data)
    return js

def send_request(endpoint, params=None):
    if params:
        url = "%s?%s" % (endpoint, urlencode(params))
    else:
        url = endpoint
    req = request.Request(url)
    resp = request.urlopen(req)
    resp_body = resp.read()
    data = json.loads(resp_body)
    return data

def get_underscore_casing(*args):
    full = ''
    for arg in args:
        full = full + arg[0].upper() + arg[1:]
    full = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', full)
    full = re.sub('([a-z0-9])([A-Z])', r'\1_\2', full).lower()
    return full

def generate_random_string(length=None):
    if not length: length=random.randint(4,10)
    letters = string.ascii_lowercase
    result = ''.join(random.choice(letters) for _ in range(length))
    return result
