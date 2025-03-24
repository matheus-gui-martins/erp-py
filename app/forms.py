from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models import User

class RegistrationForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    is_admin = SelectField('Acesso', choices=[('admin', 'Admin'), ('user', 'Usuário')], validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Cadastrar')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Lembrar Acesso')
    submit = SubmitField('Entrar')

class UploadDocumentForm(FlaskForm):
    document = FileField('Documento', validators=[FileRequired(), FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'png'], 'Apenas documentos!')])
    submit = SubmitField('Enviar')

class ConcessionariaForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Cadastrar')

class ProdutoForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Descrição')
    submit = SubmitField('Cadastrar')

class DocumentStatusForm(FlaskForm):
    status = SelectField('Status', choices=[('Em espera', 'Em espera'), ('Aceito', 'Aceito'), ('Rejeitado', 'Rejeitado')])
    concessionaria = SelectField('Concessionária', coerce=int)
    produto = SelectField('Produto', coerce=int)
    comments = TextAreaField('Comentários')
    submit = SubmitField('Atualizar')