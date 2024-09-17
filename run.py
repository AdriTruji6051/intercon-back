from app import create_app
from flask_cors import CORS

app = create_app()
CORS(app, supports_credentials=True)

if __name__ == '__main__':
    host = app.config.get('HOST', '127.0.0.1') 
    port = app.config.get('PORT', 5000)        

    app.run(host=host, port=port)

