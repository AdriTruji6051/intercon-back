#Este metodo de acceso por abrir coneccion, query, cambios, commit y cerrar lo hace bastante mas lento, 
#pero al ser un proceso de un solo uso me facilita el mudar la base de datos de FDB a sqlite mediante un 
#codigo mas limpio 

import fdb
import ctypes
import sqlite3

def fdbQuery(query)-> list:
    ctypes.cdll.LoadLibrary('./fbclient.dll')
    con =  fdb.connect(
        dsn='PDVDATA.fdb', 
        user='SYSDBA', 
        password='masterkey',
        charset='NONE'
    )

    cur = con.cursor()
    cur.execute(query)

    queryResult = cur.fetchall()

    cur.close()
    con.close()

    return queryResult

def sqlite3Query(query) -> list:
    conSQL = sqlite3.connect("./data_base.db")
    cursorSQL = conSQL.cursor()
    queryResult = cursorSQL.execute(query)
    conSQL.commit()
    conSQL.close()

    return queryResult

def sqlite3QueryParams(query, params) -> list:
    conSQL = sqlite3.connect("./data_base.db")
    cursorSQL = conSQL.cursor()
    queryResult = cursorSQL.execute(query, params)
    conSQL.commit()
    conSQL.close()

    return queryResult

def sqlite3_Several_Querys(query, paramsArray):
    conSQL = sqlite3.connect("./data_base.db")
    cursorSQL = conSQL.cursor()
    queryResult = []

    for params in paramsArray:
        try:
            queryResult.append(cursorSQL.execute(query, params))
        except Exception as e:
            print('-------------------------------------------->')
            print(f'Error al insertar el registro: "{params}"')
            print(e)

    conSQL.commit()
    conSQL.close()

    return queryResult

def productosParser() -> None:
    print('Exportando productos...')
    sqlite3Query('DROP TABLE IF EXISTS products;')
    sqlite3Query('CREATE TABLE "products" ("code" VARCHAR(50), "description" TEXT, "saleType" BLOB, "cost" REAL, "salePrice" REAL, "department" INTEGER, "wholesalePrice" REAL, "priority" INTEGER, "inventory" REAL, "modifiedAt" TEXT, "profitMargin" INTEGER, PRIMARY KEY("code"));')

    sqlQuery = 'INSERT INTO products (code,description,saleType,cost, salePrice,department,wholesalePrice,priority,inventory,modifiedAt,profitMargin) VALUES (?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?);'
    cur = fdbQuery('SELECT CODIGO, DESCRIPCION, TVENTA, PCOSTO, PVENTA, DEPT, MAYOREO, IPRIORIDAD, DINVENTARIO, CHECADO_EN, PORCENTAJE_GANANCIA FROM PRODUCTOS;')
    
    sqlite3_Several_Querys(sqlQuery, cur)

def ventaTicketsParser() -> None:
    print('Exportando tickets...')
    sqlite3Query('DROP TABLE IF EXISTS tickets;')
    sqlite3Query('CREATE TABLE "tickets" ("ID" INTEGER, "createdAt" TEXT, "subTotal" REAL, "total" REAL, "profit" REAL, "articleCount" INTEGER, "notes" BLOB, PRIMARY KEY("ID" AUTOINCREMENT));')

    sqlQuery = 'INSERT INTO tickets (ID,createdAt,subTotal,total,profit,articleCount,notes) VALUES (?, ?, ?, ?, ?, ?, ?);'

    cur = fdbQuery('SELECT ID, CREADO_EN, SUBTOTAL, TOTAL, GANANCIA, NUMERO_ARTICULOS, NOTAS FROM VENTATICKETS;')

    sqlite3_Several_Querys(sqlQuery, cur)

def ventaTicketsArticulosParser():
    print('Exportando productos vendidos...')
    sqlite3Query('DROP TABLE IF EXISTS ticketsProducts;')
    sqlite3Query('CREATE TABLE "ticketsProducts" ("ID" INTEGER, "ticketId" INTEGER, "code" VARCHAR(50), "description" TEXT, "cantity" REAL, "profit" REAL, "paidAt" TEXT, "isWholesale" TEXT, "usedPrice" REAL, PRIMARY KEY("ID" AUTOINCREMENT));')

    sqlQuery = 'INSERT INTO ticketsProducts (ID, ticketId, code, description, cantity, profit, paidAt, isWholesale, usedPrice) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);'

    cur = fdbQuery('SELECT ID, TICKET_ID, PRODUCTO_CODIGO, PRODUCTO_NOMBRE, CANTIDAD, GANANCIA, PAGADO_EN, USA_MAYOREO, PRECIO_USADO FROM VENTATICKETS_ARTICULOS;')

    sqlite3_Several_Querys(sqlQuery, cur)
        
try:
    print('CHAMBEANDO ANDAMOS V5.1')
    ventaTicketsArticulosParser()
    productosParser()    
    ventaTicketsParser()
except Exception as e:
    print(e)
finally:
    print('Finalizado...')