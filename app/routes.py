from app.models import get_pdv_db, close_pdv_db, get_products_by_description, insert_history_register
from app.helpers import create_ticket_struct, get_printers, open_drawer, send_ticket_to_printer
from flask import jsonify, request, Blueprint, render_template
from flask_jwt_extended import create_access_token, jwt_required
from datetime import datetime
from urllib.parse import unquote

routes = Blueprint('routes', __name__)
today = datetime.now().strftime('%Y-%m-%d')
PRINTERS_ON_WEB = {}


@routes.route('/')
@routes.route('/dashboard')
@routes.route('/<path:path>')
@routes.route('/dashboard/<path:path>')
def serve_index(path=None):
    print(path)
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
    
@routes.route('/api/init/new/', methods=['GET'])
@jwt_required()
def initPc():
    try:
        client_ip = request.remote_addr
        client_printers = get_printers(ipv4=client_ip)
        global PRINTERS_ON_WEB
        PRINTERS_ON_WEB.update(client_printers)
    except Exception as e:
        return jsonify({'printers': 'Not found printers there!'}), 404
    finally:
        return jsonify({'printers': 'loaded'})
    
@routes.route('/api/get/printers/', methods=['GET'])
@jwt_required()
def getPrinters():
    printers = []
    for key in PRINTERS_ON_WEB:
        if PRINTERS_ON_WEB[key]['isdefault'] == True and PRINTERS_ON_WEB[key]['ipv4'] == request.remote_addr:
            printers.insert(0, key)
        elif PRINTERS_ON_WEB[key]['isdefault'] == True:
            printers.append(key)
    return jsonify(printers)


#PRODUCTS MANAGEMENT
@routes.route('/api/get/product/<string:search>', methods=['GET'])
#@jwt_required()
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

@routes.route('/api/get/products/description/<string:description>', methods=['GET'])
@jwt_required()
def getAllProducts(description):
    db = get_pdv_db()
    try: 
        query = "SELECT code, description, salePrice FROM products WHERE description LIKE ?;"
        prod = db.execute(query,[f'%{description}%']).fetchall()

        if prod is None:
            raise Exception
        else:
            cont = 0
            answer = []
            for row in prod:
                answer.append(dict(row))
                cont += 1
                if cont >= 50: break

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
@routes.route('/api/get/tickets/day/<string:day>', methods=['GET'])
@jwt_required()
def getTicketsByDate(day):
    #Input date format YYYY:MM:DD
    db = get_pdv_db()
    try:
        sql = 'SELECT * FROM tickets WHERE createdAt LIKE ?;'
        sqlPr = 'SELECT * FROM ticketsProducts WHERE ticketId = ?;'

        rows = db.execute(sql, [f'{day}%']).fetchall()
        answer = []

        for row in rows:
            row = dict(row)
            for key in row:
                if type(row[key]) == bytes:
                    row[key] = str(row[key])

            prodRows = db.execute(sqlPr, [row['ID']]).fetchall()
            products = []
            for prod in prodRows:
                products.append(dict(prod))
            
            row['products'] = products
            answer.append(row)

        return jsonify(answer)
    
    except Exception as e:
        print(e)
        return jsonify({'message' : 'Problems at getting tickets!'}), 400
    finally:
        close_pdv_db()

@routes.route('/api/print/ticket/id/', methods=['POST'])
@jwt_required()
def printTicketById():
    db = get_pdv_db()
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400
        
        id = data['id']
        printerName = data['printerName']
        if(printerName):
            printer = PRINTERS_ON_WEB[printerName]
            
            sql = 'SELECT * FROM tickets WHERE ID = ?;'
            sqlPr = 'SELECT * FROM ticketsProducts WHERE ticketId = ?;'

            row = dict(db.execute(sql, [id]).fetchone())
            prodRows = db.execute(sqlPr, [id]).fetchall()

            products = []
            for prod in prodRows:
                prod = dict(prod)
                prod['import'] = prod['cantity'] * prod['usedPrice']
                products.append(prod)
            
            ticketStruct = create_ticket_struct(products=products, total=row['total'], subtotal=row['subTotal'], notes=row['notes'], date=row['createdAt'], productCount=row['articleCount'], wholesale=row['discount'])
            send_ticket_to_printer(ticket_struct=ticketStruct, printer=printer, open_drawer=False)

        return jsonify({'message' : 'Succesfull ticket reprint!'})
    
    except Exception as e:
        print('Exception -> ',e)
        return jsonify({'message' : 'Problems at getting tickets!'}), 400
    finally:
        close_pdv_db()


#TICKET CRUD
@routes.route('/api/create/ticket/', methods=['POST'])
@jwt_required()
def createTicket():
    db = get_pdv_db()
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400
        
        #Keys: products,total, paidWith, notes, willPrint
        date = datetime.now()

        createAt = date.strftime('%Y-%m-%d %H:%M:%S')
        printerName = data['printerName']
        willPrint = data['willPrint']
        wholesale = data['wholesale']
        subtotal = data['total']
        total = data['paidWith']
        notes = data['notes']
        productsCount = data['productsCount']

        profitTicket = 0

        ticketId = dict(db.execute('SELECT MAX (ID) FROM tickets;').fetchone())['MAX (ID)']
        queryTicktProd = 'INSERT INTO ticketsProducts (ticketId, code, description, cantity, profit, paidAt, isWholesale, usedPrice) values (?,?,?,?,?,?,?,?);'
        queryTickt = 'INSERT INTO tickets (ID, createdAt, subTotal, total, profit, articleCount, notes, discount) values (?,?,?,?,?,?,?,?);'

        if(ticketId):
            ticketId += 1
        else:
            ticketId = 1

        for prod in data['products']:
            profit = 0
            if 'wholesalePrice' in prod: prod['wholesalePrice'] = prod['wholesalePrice'] if prod['wholesalePrice'] else prod['salePrice']
            else: prod['wholesalePrice'] = prod['salePrice']

            if(prod['cost']): profit = ( (prod['wholesalePrice'] * 100) / prod['cost'] ) - 100 if wholesale else ( prod['salePrice'] * 100) /  (prod['cost']) - 100
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
            
            profitTicket += round(( prod['wholesalePrice'] * (profit /100)) * prod['cantity'] ) if wholesale else round(( prod['salePrice'] * (profit / 100)) * prod['cantity'] )
            db.execute(queryTicktProd, params)
        
        
        params = [
            ticketId,
            createAt,
            subtotal,
            total,
            profitTicket,
            productsCount,
            notes,
            wholesale
        ]

        db.execute(queryTickt, params)
        db.commit()

        if(willPrint and printerName):
            createAt = date.strftime('%d-%m-%Y %H:%M')
            ticketStruct = create_ticket_struct(products=data['products'], total=total, subtotal=subtotal,notes=notes, date=createAt, productCount=productsCount, wholesale=wholesale )
            printer = PRINTERS_ON_WEB[printerName]

            send_ticket_to_printer(ticket_struct=ticketStruct, printer=printer, open_drawer=True)

        if(not willPrint and printerName):
            printer = PRINTERS_ON_WEB[printerName]
            open_drawer(printer=printer)
        
        return jsonify({'folio' : ticketId})
    except Exception as e:
        print(e)
        return jsonify({'message' : 'Problems at updating database!'}), 400
    finally:
        close_pdv_db()


#TO DO: CHAMBEAR EN ACTUALIZAR EL TICKET Y SUS PRODUCTOS
@routes.route('/api/update/ticket/', methods=['PUT'])
@jwt_required()
def updateTicket():
    db = get_pdv_db()
    try:
        data = dict(request.get_json())

        if data is None:
            return jsonify({'message' : 'Not data sended'}), 400
        
        ticketID = data['ID']
        products = data['products']

        db.execute('UPDATE tickets SET profit = ?, discount = ?, subTotal = ?, articleCount = ? WHERE ID = ?;',[
            data['profit'],
            data['discount'],
            data['subTotal'],
            data['articleCount'],
            ticketID
        ])
        
        rows = db.execute('SELECT ID FROM ticketsProducts WHERE ticketId = ?;', [ticketID])
        prodIDs = set()
        for row in rows:
            prodIDs.add(dict(row)['ID'])

        for prod in products:
            db.execute('UPDATE ticketsProducts SET cantity = ? WHERE ID = ?;', [
                prod['cantity'],
                prod['ID']
            ])
            prodIDs.discard(prod['ID'])
        
        for id in prodIDs:
            db.execute('UPDATE ticketsProducts SET ticketId = ? WHERE ID = ?;', [ticketID * -1,id])
        
        db.commit()

        return jsonify({'message' : 'Ticket updated!'})
    except Exception as e:
        return jsonify({'message' : 'Problems at updating tickets!'}), 400
    finally:
        close_pdv_db()