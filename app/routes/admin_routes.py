import os
from flask import Blueprint, render_template, url_for, flash, redirect, request, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Document, Concessionaria, Produto
from app.forms import RegistrationForm, ConcessionariaForm, ProdutoForm, DocumentStatusForm
from werkzeug.security import generate_password_hash

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@admin.route('/admin/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('Acesso restrito para administradores', 'danger')
        return redirect(url_for('user.dashboard'))
    documents = Document.query.order_by(Document.upload_date.desc()).all()
    return render_template('admin/dashboard.html', documents=documents, title='Admin Dashboard')

@admin.route('/admin/register', methods=['GET', 'POST'])
@login_required
def register_user():
    if not current_user.is_admin:
        flash('Acesso restrito para administradores', 'danger')
        return redirect(url_for('user.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password,
            is_admin=form.is_admin.data
        )
        db.session.add(user)
        db.session.commit()
        flash(f'Conta criada para {form.name.data}!', 'success')
        return redirect(url_for('admin.users_list'))
    return render_template('admin/register.html', title='Cadastrar Usuário', form=form)

@admin.route('/admin/users')
@login_required
def users_list():
    if not current_user.is_admin:
        flash('Acesso restrito para administradores', 'danger')
        return redirect(url_for('user.dashboard'))
    users = User.query.all()
    return render_template('admin/users.html', title='Usuários', users=users)

@admin.route('/admin/concessionarias', methods=['GET', 'POST'])
@login_required
def concessionarias():
    if not current_user.is_admin:
        flash('Acesso restrito para administradores', 'danger')
        return redirect(url_for('user.dashboard'))
    
    form = ConcessionariaForm()
    if form.validate_on_submit():
        concessionaria = Concessionaria(
            name=form.name.data,
            email=form.email.data
        )
        db.session.add(concessionaria)
        db.session.commit()
        flash(f'Concessionária {form.name.data} cadastrada!', 'success')
        return redirect(url_for('admin.concessionarias'))
    
    concessionarias_list = Concessionaria.query.all()
    return render_template('admin/concessionarias.html', title='Concessionárias', 
                           concessionarias=concessionarias_list, form=form)

@admin.route('/admin/produtos', methods=['GET', 'POST'])
@login_required
def produtos():
    if not current_user.is_admin:
        flash('Acesso restrito para administradores', 'danger')
        return redirect(url_for('user.dashboard'))
    
    form = ProdutoForm()
    if form.validate_on_submit():
        produto = Produto(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(produto)
        db.session.commit()
        flash(f'Produto {form.name.data} cadastrado!', 'success')
        return redirect(url_for('admin.produtos'))
    
    produtos_list = Produto.query.all()
    return render_template('admin/produtos.html', title='Produtos', 
                           produtos=produtos_list, form=form)

@admin.route('/admin/document/<int:document_id>', methods=['GET', 'POST'])
@login_required
def document_details(document_id):
    if not current_user.is_admin:
        flash('Acesso restrito para administradores', 'danger')
        return redirect(url_for('user.dashboard'))
    
    document = Document.query.get_or_404(document_id)
    form = DocumentStatusForm()
    
    # Populate dropdown choices
    form.concessionaria.choices = [(0, 'Selecione...')] + [(c.id, c.name) for c in Concessionaria.query.all()]
    form.produto.choices = [(0, 'Selecione...')] + [(p.id, p.name) for p in Produto.query.all()]
    
    if form.validate_on_submit():
        document.status = form.status.data
        document.comments = form.comments.data
        
        # Only update if selected
        if form.concessionaria.data != 0:
            document.concessionaria_id = form.concessionaria.data
        if form.produto.data != 0:
            document.produto_id = form.produto.data
        
        db.session.commit()
        flash('Documento atualizado com sucesso!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    # Populate form with existing data
    form.status.data = document.status
    form.comments.data = document.comments
    if document.concessionaria_id:
        form.concessionaria.data = document.concessionaria_id
    if document.produto_id:
        form.produto.data = document.produto_id
    
    return render_template('admin/document_details.html', title='Detalhes do Documento', 
                          document=document, form=form)

@admin.route('/admin/download/<filename>')
@login_required
def download_file(filename):
    if not current_user.is_admin:
        flash('Acesso restrito para administradores', 'danger')
        return redirect(url_for('user.dashboard'))
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)