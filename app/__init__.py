from flask import Flask
from flask_jwt_extended import JWTManager
from .models import close_db

def create_app():
    app = Flask(__name__)

    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here'  # Cambia esta clave a una clave segura

    # Inicializa JWTManager Para el manejo de tokens
    jwt = JWTManager(app)
    # Configuraciones
    app.config.from_pyfile('../instance/config.py')

    # Registro de rutas
    from .routes import routes
    app.register_blueprint(routes)

    #Cerramos la base de datos
    @app.teardown_appcontext
    def teardown_db(exception=None):
        close_db()

    return app
