from flask import jsonify, request, Blueprint
from flask_jwt_extended import create_access_token, jwt_required
from app.models import get_pdv_db, close_pdv_db, get_products_by_description

routes = Blueprint('routes', __name__)

@routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == 'admin':
        access_token = create_access_token(identity=username)
        return jsonify({'login': 'exitoso', 'token': access_token}), 200
    else:
        return jsonify({'login': 'fallido', 'message': 'Credenciales incorrectas'}), 401

@routes.route('/api/get/product/<string:search>', methods=['GET'])
# @jwt_required()
def getProduct(search):
    db = get_pdv_db()
    try:
        query = "SELECT * FROM products WHERE code = ?"
        prod = db.execute(query, [search]).fetchone()

        if prod is None:
            query = 'SELECT * FROM products WHERE description LIKE ?'
            prod = get_products_by_description(db=db, query=query, params=search)

            if len(prod) == 0: 
                return jsonify({"message": "Product not found"}), 404
            else:
                return jsonify(prod)
        else:
            return jsonify([dict(prod)])
    except Exception as e:
        print(e)
    finally:
        close_pdv_db()
    
@routes.route('/api/get/product/id/<string:search>', methods=['GET'])
#@jwt_required()
def getProductById(search):
    db = get_pdv_db()
    try: 
        query = "SELECT * FROM products WHERE code = ?"
        prod = db.execute(query, [search]).fetchone()

        if prod is None:
            return jsonify({"message": "Product not found"}), 404
        else:
            return jsonify(dict(prod))
    except Exception as e:
        print(e)
    finally:
        close_pdv_db()
