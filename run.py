import socket
from app.app import create_app
from flask_cors import CORS

app = create_app()

CORS(app, supports_credentials=True)

def get_local_ip() -> str:
    # Crear una conexión a una dirección IP externa (no se enviará ningún dato)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Intentar conectarse a una IP pública (Google DNS en este caso)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception as e:
        local_ip = 'No se pudo obtener la IP'
    finally:
        s.close()
    return local_ip

if __name__ == '__main__':
    host = '127.0.0.1' #get_local_ip()
    port = 5000   

    app.run(host=host, port=port)


    