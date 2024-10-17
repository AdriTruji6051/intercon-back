import os
import re
import sys
import time
import webbrowser
import threading
import socket
from app.app import create_app
from flask_cors import CORS
from printer_service.printerServ import run_printer_service

app = create_app()

CORS(app, supports_credentials=True)

def get_local_ip() -> str:
    try:
        # Obtener el nombre de host local
        hostname = socket.gethostname()
        # Obtener la IP asociada al nombre de host
        local_ip = socket.gethostbyname(hostname)
    except Exception as e:
        local_ip = '127.0.0.1'
    return local_ip

def get_data_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # Si está ejecutando desde un ejecutable generado por PyInstaller
        base_path = sys._MEIPASS
    else:
        # Si se está ejecutando en modo normal (desarrollo)
        base_path = os.path.dirname(__file__)
    
    return os.path.join(base_path, relative_path)


def openPDV():
    time.sleep(2)
    webbrowser.open(f'http://{get_local_ip()}:5000/')

def refreshApiIp():
    #Open js file
    jsRoute = get_data_path('app/static')
    jsRoute = os.path.join(jsRoute, 'main.js')
    with open(jsRoute, 'r', encoding='utf-8') as file:
        content = file.read()

    #Looking for the old IP
    regex = r"http:\/\/(?:\d{1,3}\.){3}\d{1,3}:5000"
    previousIp = re.findall(regex, content)[0]
    newIp = f'http://{get_local_ip()}:5000'

    if(previousIp == newIp):
        print('IP DO NOT NEED CHANGES!')
        return

    newFile = content.replace(previousIp, newIp)
    
    with open(jsRoute, 'w', encoding='utf-8') as file:
        file.write(newFile)
 
    print('SUCCESFULL IP CHANGE!')

if __name__ == '__main__':
    refreshApiIp()
    host = '127.0.0.1'#get_local_ip()
    port = 5000   

    #threading.Thread(target=openPDV).start()
    #threading.Thread(target=run_printer_service).start()
    app.run(host=host, port=port)


    