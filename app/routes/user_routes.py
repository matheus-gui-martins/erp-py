import os
import secrets
from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Document
from app.forms import UploadDocumentForm
from werkzeug.utils import secure_filename

user = Blueprint('user', __name__)

def save_document(form_document):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_document.filename)
    document_fn = random_hex + f_ext
    document_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document_fn)
    
    if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
        os.makedirs(current_app.config['UPLOAD_FOLDER'])
    
    form_document.save(document_path)
    return document_fn, secure_filename(form_document.filename)

@user.route('/')
@user.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.upload_date.desc()).all()
    return render_template('user/dashboard.html', documents=documents, title='Dashboard')

@user.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_document():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    form = UploadDocumentForm()
    if form.validate_on_submit():
        document_filename, original_filename = save_document(form.document.data)
        document = Document(
            filename=document_filename,
            original_filename=original_filename,
            user_id=current_user.id
        )
        db.session.add(document)
        db.session.commit()
        flash('Documento enviado com sucesso!', 'success')
        return redirect(url_for('user.dashboard'))
    return render_template('user/upload.html', title='Enviar Documento', form=form)