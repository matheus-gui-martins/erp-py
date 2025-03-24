from app import create_app, db
from app.models import User, Document, Concessionaria, Produto

app = create_app()

with app.app_context():
    print("Excluindo todas as tabelas...")
    db.drop_all()
    
    print("Criando todas as tabelas novamente...")
    db.create_all()
    
    print("Banco de dados recriado com sucesso!")