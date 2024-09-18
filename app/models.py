import sqlite3
from flask import g

DATABASE = './db/data_base.sqlite3'

def get_pdv_db() -> object:
    try:
        if 'pdv_db' not in g:
            g.db = sqlite3.connect(DATABASE)
            g.db.row_factory = sqlite3.Row
        return g.db
    
    except Exception as e:
        raise(e)

def close_pdv_db():
    try:
        db = g.pop('pdv_db', None)
        if db is not None:
            db.close()

    except Exception as e:
        raise(e)
    

def get_products_by_description(db = object, query = str, params = str) -> list:
    try:
        params = params.upper()
        rows = db.execute(query, [f'%{params}%']).fetchall()
        rows = [dict(row) for row in rows]

        prod = []
        insertIndex = 0
        for row in rows:
            des = row['description'][:len(params)].upper()
            if des == params: 
                prod.insert(insertIndex, row)
                insertIndex += 1
            else: 
                prod.append(row) 

        return prod
    
    except Exception as e:
        raise(e)
