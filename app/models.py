from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    documents = db.relationship('Document', backref='author', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'

class Concessionaria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(2), nullable=True)
    documents = db.relationship('Document', backref='concessionaria', lazy=True)

    def __repr__(self):
        return f'<Concessionaria {self.name}>'

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f"Produto('{self.name}')"

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    original_filename = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Em espera')  # 'Em espera', 'Aceito', 'Rejeitado'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    concessionaria_id = db.Column(db.Integer, db.ForeignKey('concessionaria.id'), nullable=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=True)
    comments = db.Column(db.Text)
    
    def __repr__(self):
        return f"Document('{self.original_filename}', '{self.status}')"