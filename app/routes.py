from app.models import get_pdv_db, close_pdv_db, get_products_by_description, get_hist_db, close_hist_db, insert_history_register
from flask import jsonify, request, Blueprint
from flask_jwt_extended import create_access_token, jwt_required
from datetime import datetime
import json

routes = Blueprint('routes', __name__)
today = datetime.now().strftime('%Y-%m-%d')

@routes.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == 'admin':
        access_token = create_access_token(identity=username)
        return jsonify({'login': 'exitoso', 'token': access_token}), 200
    else:
        return jsonify({'login': 'fallido', 'message': 'Credenciales incorrectas'}), 401


#PRODUCTS MANAGEMENT
@routes.route('/api/get/product/<string:search>', methods=['GET'])
# @jwt_required()
def getProduct(search):
    db = get_pdv_db()
    try:
        query = "SELECT * FROM products WHERE code = ?"
        prod = db.execute(query, [search]).fetchone()

        if prod is None:
            query = 'SELECT * FROM products WHERE description LIKE ?;'
            prod = get_products_by_description(db=db, query=query, params=search)

            if len(prod) == 0: 
                raise Exception
            else:
                return jsonify(prod)
        else:
            return jsonify([dict(prod)])
    except Exception as e:
        print(e)
        return jsonify({"message": "Product not found"}), 404
    finally:
        close_pdv_db()
    
@routes.route('/api/get/product/id/<string:search>', methods=['GET'])
#@jwt_required()
def getProductById(search):
    db = get_pdv_db()
    try: 
        query = "SELECT * FROM products WHERE code = ?;"
        prod = db.execute(query, [search]).fetchone()

        if prod is None:
            raise Exception
        else:
            return jsonify(dict(prod))
    except Exception as e:
        print(e)
        return jsonify('{"message": "Product not found"}'), 404
    finally:
        close_pdv_db()

#PRODUCTS CRUD ----------------->
@routes.route('/api/create/product/', methods=['POST'])
@jwt_required()
def createProduct():
    db = get_pdv_db()

    try:
        data = dict(request.get_json())
    
        if data is None:
            raise Exception('Not data recived!')

        query = 'SELECT * FROM products WHERE code = ?;'
        row = db.execute(query, [data.get('code')]).fetchone()

        if row is not None:
            raise Exception('Product already exist!')
        
        #Creamos el producto
        query = 'INSERT INTO products (code, description, saleType, cost, salePrice, department, wholesalePrice, priority, inventory, profitMargin, modifiedAt) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
        keys = ["code", "description", "saleType", "cost", "salePrice", "department", "wholesalePrice", "priority", "inventory", "profitMargin"]
        params = [data[key] for key in keys]
        params.append(today)
        db.execute(query, params)
        db.commit()

        #Insertamos el registro en el historial
        insert_history_register(data=data, today=today, method='POST')

        return jsonify({'message' : 'Product succesfully created!'})
            
    except Exception as e:
        print(e)
        return jsonify({'message' : f'{str(e)}'}), 404
    finally:
        close_pdv_db()
        close_hist_db()
    
@routes.route('/api/update/product/', methods=['PUT'])
@jwt_required()
def updateProduct():
    db = get_pdv_db()

    try:
        data = dict(request.get_json())
    
        if data is None:
            raise Exception('Not data recived!')

        query = 'SELECT * FROM products WHERE code = ?;'
        row = db.execute(query, [data.get('code')]).fetchone()

        if row is None:
            raise Exception('Product not exist!')
        
        #Creamos el producto
        query = 'UPDATE products SET description = ?, saleType = ?, cost = ?, salePrice = ?, department = ?, wholesalePrice = ?, priority = ?, inventory = ?, profitMargin = ?, modifiedAt = ? WHERE code = ?;'
        keys = ["description", "saleType", "cost", "salePrice", "department", "wholesalePrice", "priority", "inventory", "profitMargin"]
        params = [data[key] for key in keys]
        params.append(today)
        params.append(data['code'])
        db.execute(query, params)
        db.commit()

        #Insertamos el registro en el historial
        insert_history_register(data=data, today=today, method='PUT')

        return jsonify({'message' : 'Product succesfully updated!'})
            
    except Exception as e:
        print(e)
        return jsonify({'message' : f'{str(e)}'}), 404
    finally:
        close_pdv_db()
        close_hist_db()

@routes.route('/api/delete/product/id/<string:id>', methods=['DELETE'])
@jwt_required()
def deleteProductById(id):
    db = get_pdv_db()

    try:
        query = 'SELECT * FROM products WHERE code = ?;'
        row = db.execute(query, [id]).fetchone()

        if row is None:
            raise Exception('Code not in products!..') 

        #Borramos el producto 
        query = 'DELETE FROM products WHERE code = ?;'
        db.execute(query, [id])
        db.commit()
        
        #Insertamos el registro en el historial
        data = dict(row)
        insert_history_register(data=data, today=today, method='DELETE')

        return jsonify({'message' : f'Succesfully deleted product with code = {id}'})
    
    except Exception as e:
        print(e)
        return jsonify({'message' : f'Not found product with code = {id}'}), 404
    finally:
        close_pdv_db()