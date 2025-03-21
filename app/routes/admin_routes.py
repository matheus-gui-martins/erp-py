import os
from flask import Blueprint, render_template, url_for, flash, redirect, request, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Document, Concessionaria, Produto
from app.forms import RegistrationForm, ConcessionariaForm, ProdutoForm, DocumentStatusForm
from werkzeug.security import generate_password_hash

admin = Blueprint('admin', __name__)
auth_bp = Blueprint('auth', __name__)

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
    
    # Buscar o documento no banco de dados
    document = Document.query.get_or_404(document_id)
    old_status = document.status  # Salvar o status antigo para comparação
    form = DocumentStatusForm()
    
    # Preencher as opções dos dropdowns
    form.concessionaria.choices = [(0, 'Selecione...')] + [(c.id, c.name) for c in Concessionaria.query.all()]
    form.produto.choices = [(0, 'Selecione...')] + [(p.id, p.name) for p in Produto.query.all()]
    
    if form.validate_on_submit():
        # Atualizar os dados do documento
        document.status = form.status.data
        document.comments = form.comments.data
        
        # Atualizar concessionária e produto, se selecionados
        if form.concessionaria.data != 0:
            document.concessionaria_id = form.concessionaria.data
        if form.produto.data != 0:
            document.produto_id = form.produto.data
        
        db.session.commit()
        
        # Enviar notificações por e-mail se o status foi alterado
        if old_status != document.status:
            user = User.query.get(document.user_id)
            
            # Notificar o usuário
            subject = f"Atualização de status do documento: {document.original_filename}"
            message = f"""
            <html>
                <body>
                    <h2>Atualização de Status do Documento</h2>
                    <p>Olá {user.name},</p>
                    <p>O status do seu documento <strong>{document.original_filename}</strong> foi atualizado para <strong>{document.status}</strong>.</p>
                    
                    {'<p><strong>Comentários:</strong> ' + document.comments + '</p>' if document.comments else ''}
                    
                    <p>Acesse sua conta para mais detalhes.</p>
                    <p>Atenciosamente,<br>Equipe de Administração</p>
                </body>
            </html>
            """
            send_email_notification(user.email, subject, message)
            
            # Notificar a concessionária, se aplicável
            if document.concessionaria_id and document.status == 'Aceito':
                concessionaria = Concessionaria.query.get(document.concessionaria_id)
                
                subject_conc = f"Novo documento atribuído: {document.original_filename}"
                message_conc = f"""
                <html>
                    <body>
                        <h2>Novo Documento Atribuído</h2>
                        <p>Olá,</p>
                        <p>Um novo documento foi atribuído à sua concessionária.</p>
                        <p><strong>Documento:</strong> {document.original_filename}</p>
                        <p><strong>Enviado por:</strong> {user.name}</p>
                        
                        {'<p><strong>Comentários:</strong> ' + document.comments + '</p>' if document.comments else ''}
                        
                        <p>Acesse o sistema para mais detalhes.</p>
                        <p>Atenciosamente,<br>Equipe de Administração</p>
                    </body>
                </html>
                """
                send_email_notification(concessionaria.email, subject_conc, message_conc)
        
        flash('Documento atualizado com sucesso!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    # Preencher o formulário com os dados existentes do documento
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

@auth_bp.route('/concessionarias', methods=['GET', 'POST'])
def concessionarias():
    return render_template('auth/concessionarias.html')

@auth_bp.route('/produtos', methods=['GET', 'POST'])
def produtos():
    return render_template('auth/produtos.html')

# Adicionar ao arquivo app/routes/admin_routes.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_email_notification(recipient_email, subject, message):
    """
    Enviar uma notificação por e-mail para o usuário ou concessionária
    """
    sender_email = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(message, 'html'))
    
    try:
        server = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")
        return False

# Atualizar a rota document_details para incluir notificação por e-mail
@admin.route('/admin/document/<int:document_id>', methods=['GET', 'POST'])
@login_required
def document_details(document_id):
    if not current_user.is_admin:
        flash('Acesso restrito para administradores', 'danger')
        return redirect(url_for('user.dashboard'))
    
    document = Document.query.get_or_404(document_id)
    old_status = document.status
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
        
        # Enviar e-mail se o status for alterado
        if old_status != document.status:
            user = User.query.get(document.user_id)
            
            subject = f"Atualização de status do documento: {document.original_filename}"
            
            message = f"""
            <html>
                <body>
                    <h2>Atualização de Status do Documento</h2>
                    <p>Olá {user.name},</p>
                    <p>O status do seu documento <strong>{document.original_filename}</strong> foi atualizado para <strong>{document.status}</strong>.</p>
                    
                    {'<p><strong>Comentários:</strong> ' + document.comments + '</p>' if document.comments else ''}
                    
                    <p>Acesse sua conta para mais detalhes.</p>
                    <p>Atenciosamente,<br>Equipe de Administração</p>
                </body>
            </html>
            """
            
            send_email_notification(user.email, subject, message)
            
            # Se estiver associado a uma concessionária, notificar também
            if document.concessionaria_id and document.status == 'Aceito':
                concessionaria = Concessionaria.query.get(document.concessionaria_id)
                
                subject_conc = f"Novo documento atribuído: {document.original_filename}"
                
                message_conc = f"""
                <html>
                    <body>
                        <h2>Novo Documento Atribuído</h2>
                        <p>Olá,</p>
                        <p>Um novo documento foi atribuído à sua concessionária.</p>
                        <p><strong>Documento:</strong> {document.original_filename}</p>
                        <p><strong>Enviado por:</strong> {user.name}</p>
                        
                        {'<p><strong>Comentários:</strong> ' + document.comments + '</p>' if document.comments else ''}
                        
                        <p>Acesse o sistema para mais detalhes.</p>
                        <p>Atenciosamente,<br>Equipe de Administração</p>
                    </body>
                </html>
                """
                
                send_email_notification(concessionaria.email, subject_conc, message_conc)
        
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