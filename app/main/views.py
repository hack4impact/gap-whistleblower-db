from flask import Blueprint, request, render_template, redirect, url_for
from random import randint
from time import sleep
from app.models import EditableHTML, Document, Saved, User
from flask_login import current_user, login_required
# import flask_whooshalchemyplus as whooshalchemy
# from flask_whooshee import Whooshee
from app.main.forms import SaveForm, UnsaveForm
from app import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('main/index.html', search_results=[])


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template(
        'main/about.html', editable_html_obj=editable_html_obj)

@main.route('/resource/saved/<int:id>', methods=['GET', 'POST'])
@login_required
def resource_saved(id):
    return resource(id, from_saved=True)

@main.route('/resource/<int:id>', methods=['GET', 'POST'])
def resource(id, from_saved=False):
    resource = Document.query.get(id)
    user_id = getattr(current_user, 'id', None)
    saved_objs = Saved.query.filter_by(user_id=user_id, doc_id=id)
    saved = bool(user_id) and bool(saved_objs.all())
    form = UnsaveForm() if saved else SaveForm()
    if form.validate_on_submit():
        if saved:
            saved_objs.delete()
        else:
            saved = Saved(user_id=user_id, doc_id=id)
            db.session.add(saved)
        db.session.commit()
        return redirect(url_for('main.resource' if not from_saved else 'main.resource_saved', id=id))
    return render_template(
        'main/resource.html', resource=resource, user_id=user_id, saved=saved, form=form, from_saved=from_saved
    )

@main.route('/saved')
@login_required
def review_saved():
    user_id = current_user.id
    user = User.query.get(user_id)
    saved = user.saved
    return render_template('main/review_saved.html', saved=saved)