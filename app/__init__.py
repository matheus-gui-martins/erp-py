from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import os

db = SQLAlchemy()
Migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
    app.config.from_object(config_class)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    db.init_app(app)
    login_manager.init_app(app)
    Migrate.init_app(app, db)
    
    from app.routes.auth_routes import auth
    from app.routes.user_routes import user
    from app.routes.admin_routes import admin
    
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(admin)
    
    with app.app_context():
        db.create_all()
        
        # Criar usuário admin inicial se não existir
        from app.models import User
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            from werkzeug.security import generate_password_hash
            admin = User(
                name='Administrador',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
    
    return app