from flask import Flask, jsonify, request, Blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from ..models import hello
routes = Blueprint('routes', __name__)

@routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    print(username,password)

    if username == 'admin' and password == 'admin':
        access_token = create_access_token(identity=username)
        return jsonify({'login': 'exitoso', 'token': access_token}), 200
    else:
        return jsonify({'login': 'fallido', 'message': 'Credenciales incorrectas'}), 401


@routes.route('/protegido', methods=['GET'])
@jwt_required()
def protegido():
    current_user = get_jwt_identity()
    return jsonify({'response': f'Bienvenido {current_user}', 'data': {'ejemplo': 'Este es un JSON protegido'}})

@routes.route('/get/product/<string:product>', methods=['GET'])
@jwt_required()
def getProduct(product):
    # db = get_db()
    # quey = "SELECT * FROM PRODUCTOS WHERE CODIGO = ?"
    # findedProd = db.execute(quey, [product]).fetchall()
    # if findedProd is None:
    #     return jsonify({"message": "User not found"}), 404
    
    # return jsonify(dict(findedProd))
    return jsonify({"message": "User not found"})

@routes.route('/api/hello', methods=['GET'])
def hello_world():
    return {"message": "Hello, World!"}
