from app.models import get_pdv_db, close_pdv_db, get_products_by_description, get_hist_db, close_hist_db, insert_history_register
from flask import jsonify, request, Blueprint, render_template
from flask_jwt_extended import create_access_token, jwt_required
from datetime import datetime

routes = Blueprint('routes', __name__)
today = datetime.now().strftime('%Y-%m-%d')

@routes.route('/')
def serve_index():
    return render_template('index.html')

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
@jwt_required()
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

@routes.route('/api/get/all/products', methods=['GET'])
@jwt_required()
def getAllProducts():
    db = get_pdv_db()
    try: 
        query = "SELECT description FROM products;"
        prod = db.execute(query).fetchall()

        if prod is None:
            raise Exception
        else:
            answer = []
            for row in prod:
                answer.append(row[0])
            return jsonify(answer)
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

#TICKET MANAGEMENT
@routes.route('/api/create/ticket/', methods=['POST'])
@jwt_required()
def createTicket():
    db = get_pdv_db()
    try:
        data = dict(request.get_json())

        if data is None:
            print('Not data recived!')
            return jsonify({'message' : 'Not data sended'}), 400
        
        #Keys: products,total, paidWith, notes, willPrint
        date = datetime.now()

        createAt = date.strftime('%Y-%m-%d %H:%M:%S')
        wholesale = data['wholesale']
        subtotal = data['total']
        total = data['paidWith']
        notes = data['notes']
        profitTicket = 0
        articleCount = 0

        ticketId = dict(db.execute('SELECT MAX (ID) FROM tickets;').fetchone())['MAX (ID)']
        if(ticketId):
            ticketId += 1
        else:
            ticketId = 1
        
        query = 'INSERT INTO ticketsProducts (ticketId, code, description, cantity, profit, paidAt, isWholesale, usedPrice) values (?,?,?,?,?,?,?,?);'
        for prod in data['products']:
            profit = 0
            if 'wholesalePrice' in prod: prod['wholesalePrice'] = prod['wholesalePrice'] if prod['wholesalePrice'] else prod['salePrice']
            else: prod['wholesalePrice'] = prod['salePrice']

            if(prod['cost']): profit = ( (prod['salePrice'] * 100) / prod['cost'] ) - 100 if wholesale else ( prod['wholesalePrice'] * 100) /  (prod['cost']) - 100
            else: profit = 10

            params = [
                ticketId,
                prod['code'],
                prod['description'],
                prod['cantity'],
                round(profit),
                createAt,
                wholesale,
                prod['wholesalePrice'] if wholesale else prod['salePrice']
            ]

            articleCount += round(prod['cantity'])
            profitTicket += round(( prod['wholesalePrice'] * (profit /100)) * prod['cantity'] ) if wholesale else round(( prod['salePrice'] * (profit / 100)) * prod['cantity'] )
            db.execute(query, params)
        
        query = 'INSERT INTO tickets (ID, createdAt, subTotal, total, profit, articleCount, notes) values (?,?,?,?,?,?,?);'
        params = [
            ticketId,
            createAt,
            subtotal,
            total,
            profitTicket,
            articleCount,
            notes
        ]

        db.execute(query, params)
        db.commit()
        print('SUCCESFULL!')
        
        return jsonify({'message' : 'Ticket created!'})
    except Exception as e:
        print(e)
        return jsonify({'message' : 'Problems at updating database!'}), 400
    finally:
        close_pdv_db()
