from flask import Blueprint, render_template, flash, current_app, request, url_for, redirect
from flask_paginate import Pagination, get_page_parameter

from api import JsonMethods
from forms import AddApiForm, EditApiForm, AddEndpointForm, EditEndpointForm, AddFieldForm, EditFieldForm
from utils import paginate
from config import Globals

views = Blueprint('views', __name__)

@views.route('/')
def list_apis():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    apis = JsonMethods.get_apis(page=page)
    total = JsonMethods.get_apis_count().get('count')
    pagination = Pagination(
        page=page, per_page=Globals.ITEM_PER_PAGE,
        total=total, record_name='apis', css_framework='bootstrap4'
    )
    edit_api_form = EditApiForm()
    add_endpoint_form = AddEndpointForm()
    return render_template(
        'apis_listing.html', apis=apis, pagination=pagination,
        edit_api_form=edit_api_form, add_endpoint_form=add_endpoint_form
    )

@views.route('/<int:id>')
def detail_api(id):
    page = request.args.get('page', type=int, default=1)
    api = JsonMethods.get_api(id)
    endpoints = api.get('endpoints')
    total = len(endpoints)
    if total:
        try:
            endpoints = paginate(
                endpoints, Globals.ITEM_PER_PAGE,
                page, lambda x: int(x.get('id'))
            )
        except:
            flash('There is no %d pages of endpoints for API %d' % (page, api_id), 'danger')
            return redirect(url_for('views.list_endpoints'))

    pagination = Pagination(
        page=page, per_page=Globals.ITEM_PER_PAGE,
        total=total, record_name='endpoints', css_framework='bootstrap4'
    )
    edit_api_form = EditApiForm()
    add_endpoint_form = AddEndpointForm()
    edit_endpoint_form = EditEndpointForm()
    add_field_form = AddFieldForm()
    return render_template(
        'api_detailing.html', api=api, endpoints=endpoints, pagination=pagination,
        edit_api_form=edit_api_form, add_endpoint_form=add_endpoint_form,
        edit_endpoint_form=edit_endpoint_form, add_field_form=add_field_form
    )

@views.route('/search')
def search_by_tags():
    tags = request.args.get('tags')
    apis = JsonMethods.get_apis(tags=tags)
    endpoints = JsonMethods.get_endpoints(tags=tags)
    edit_api_form = EditApiForm()
    add_endpoint_form = AddEndpointForm()
    edit_endpoint_form = EditEndpointForm()
    add_field_form = AddFieldForm()
    return render_template(
        'search_by_tags.html', apis=apis, endpoints=endpoints,
        edit_api_form=edit_api_form, add_endpoint_form=add_endpoint_form,
        edit_endpoint_form=edit_endpoint_form, add_field_form=add_field_form
    )

@views.route('/add', methods=['GET', 'POST'])
def add_api():
    form = AddApiForm()
    if form.validate_on_submit():
        response = JsonMethods.add_api(
            label=form.label.data, url=form.url.data,
            description=form.description.data, tags=form.tags.data
        )
        if response.get('status') == 'ok':
            flash(response.get('message'), 'success')
            id = response.get('id')
            return redirect(url_for('views.detail_api', id=id))
        else:
            flash(response.get('message'), 'danger')
            return redirect(url_for('views.add_api'))
    return render_template('api_adding.html', form=form)

@views.route('/edit/<int:id>', methods=['POST'])
def edit_api(id):
    form = EditApiForm()
    if form.validate_on_submit():
        response = JsonMethods.edit_api(
            id, label=form.label.data, url=form.url.data,
            description=form.description.data, tags=form.tags.data
        )
        if response.get('status') == 'error':
            flash(response.get('message'), 'danger')
        else:
            flash(response.get('message'), 'success')
    else:
        flash(
            "The following errors occured while editing api #%s: %s"%
            (id, form.errors), 'danger'
        )
    return redirect(url_for('views.detail_api', id=id))

@views.route('/add_endpoint/<int:id>', methods=['POST'])
def add_endpoint(id):
    form = AddEndpointForm()
    if form.validate_on_submit():
        response = JsonMethods.add_endpoint(
            id,label=form.label.data, url=form.url.data,
            description=form.description.data, tags=form.tags.data
        )
        if response.get('status') == 'error':
            flash(response.get('message'), 'danger')
        else:
            flash(response.get('message'), 'success')
    else:
        flash(
            "The following errors occured while adding an endpoint to api #%s: %s"%
            (id, form.errors), 'danger'
        )
    return redirect(url_for('views.detail_api', id=id))

@views.route('/delete/<int:id>', methods=['POST'])
def delete_api(id):
    response = JsonMethods.delete_api(id)
    if response.get('status')=='error':
        flash(response.get('message'), 'danger')
    else:
        flash(response.get('message'), 'success')
    return redirect(url_for('views.list_apis'))

@views.route('/endpoints')
def list_endpoints():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    endpoints = JsonMethods.get_endpoints(page=page)
    total = JsonMethods.get_endpoints_count().get('count')
    pagination = Pagination(
        page=page, per_page=Globals.ITEM_PER_PAGE,
        total=total, record_name='endpoints', css_framework='bootstrap4'
    )
    edit_endpoint_form = EditEndpointForm()
    add_field_form = AddFieldForm()
    return render_template(
        'endpoints_listing.html', endpoints=endpoints, pagination=pagination,
        edit_endpoint_form=edit_endpoint_form, add_field_form=add_field_form
    )

@views.route('/edit_endpoint/<int:id>', methods=['POST'])
def edit_endpoint(id):
    form = EditEndpointForm()
    if form.validate_on_submit():
        response = JsonMethods.edit_endpoint(
            id, label=form.label.data, url=form.url.data,
            description=form.description.data, tags=form.tags.data
        )
        if response.get('status') == 'error':
            flash(response.get('message'), 'danger')
        else:
            flash(response.get('message'), 'success')
    else:
        flash(
            "The following errors occured while editing endpoint #%s: %s"%
            (id, form.errors), 'danger'
        )
    return redirect(url_for('views.detail_endpoint', id=id))

@views.route('/endpoints/delete/<int:id>', methods=['POST'])
def delete_endpoint(id):
    response = JsonMethods.delete_endpoint(id)
    if response.get('status')=='error':
        flash(response.get('message'), 'danger')
    else:
        flash(response.get('message'), 'success')
    return redirect(url_for('views.list_endpoints'))

@views.route('/endpoints/<int:id>')
def detail_endpoint(id):
    endpoint = JsonMethods.get_endpoint(id)
    add_field_form = AddFieldForm()
    edit_endpoint_form = EditEndpointForm()
    edit_field_form = EditFieldForm()
    return render_template(
        'endpoint_detailing.html', endpoint=endpoint, add_field_form=add_field_form,
        edit_endpoint_form=edit_endpoint_form, edit_field_form=edit_field_form
    )

@views.route('/endpoints/<int:id>/add_field', methods=['POST'])
def add_field(id):
    form = AddFieldForm()
    if form.validate_on_submit():
        response = JsonMethods.add_field(
            id, label=form.label.data, field_type=form.type.data,
            required=form.required.data, default=form.default.data,
            description=form.description.data
        )
        if response.get('status') == 'error':
            flash(response.get('message'), 'danger')
        else:
            flash(response.get('message'), 'success')
    else:
        flash(
            "The following errors occured while adding a field to endpoint #%s: %s" %
            (id, form.errors), 'danger'
        )

    return redirect(url_for('views.detail_endpoint', id=id))

@views.route('/fields/<int:id>/edit_field', methods=['POST'])
def edit_field(id):
    form = EditFieldForm()
    field = JsonMethods.get_field(id)
    endpoint_id = int(field.get('endpoint_id'))
    if form.validate_on_submit():
        response = JsonMethods.edit_field(
            id, label=form.label.data, field_type=form.type.data,
            required=form.required.data, default=form.default.data,
            description=form.description.data
        )
        if response.get('status') == 'error':
            flash(response.get('message'), 'danger')
        else:
            flash(response.get('message'), 'success')
    else:
        flash(
            "The following errors occured while editing field #%s: %s"%
            (id, form.errors), 'danger'
        )
    return redirect(url_for('views.detail_endpoint', id=endpoint_id))

@views.route('/fields/<int:id>/delete', methods=['POST'])
def delete_field(id):
    field = JsonMethods.get_field(id)
    endpoint_id = int(field.get('endpoint_id'))
    response =  JsonMethods.delete_field(id)
    if response.get('status')=='error':
        flash(response.get('message'), 'danger')
    else:
        flash(response.get('message'), 'success')
    return redirect(url_for('views.detail_endpoint', id=endpoint_id))
