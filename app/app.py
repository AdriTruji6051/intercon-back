from flask import Flask
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)

    app.config['JWT_SECRET_KEY'] = '0191ee57-49ca-1994-0cd6-1f77b76b7667'

    # Registro de rutas
    from app.routes import routes
    app.register_blueprint(routes)

    return app