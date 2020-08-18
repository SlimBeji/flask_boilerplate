from flask import flash, redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user

from models import db, ApiItem, Tag, Endpoint, Field

# Create customized model views class
class MyModelView(ModelView):
    column_default_sort = 'id'
    column_display_pk = True
    page_size = 20

    def is_accessible(self):
        return (
            current_user.is_active and
            current_user.is_authenticated and
            current_user.has_role('superuser')
        )

    def _handle_view(self, name, **kwargs):
        """Override builtin _handle_view in order to redirect
        users when a view is not accessible. """
        if not self.is_accessible():
            flash('You need to login as Admin to access the Backend')
            return redirect(url_for('security.logout'))

# Create Customized AdminIndexClass
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return (
                current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('superuser')
        )

    def _handle_view(self, name, **kwargs):
        """Override builtin _handle_view in order to redirect
        users when a view is not accessible. """
        if not self.is_accessible():
            flash('You need to login as a superuser to access the Backend')
            return redirect(url_for('security.logout'))

# Create admin
admin = Admin(
    name='Admin Area',
    index_view=MyAdminIndexView(),
    template_mode="bootstrap3",
    base_template='/admin/my_base.html'
)

# Add model views
admin.add_view(MyModelView(ApiItem, db.session))
admin.add_view(MyModelView(Endpoint, db.session))
admin.add_view(MyModelView(Field, db.session))
admin.add_view(MyModelView(Tag, db.session))
