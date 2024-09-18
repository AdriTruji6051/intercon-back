import sqlite3
from flask import g

DATABASE = './db/data_base.sqlite3'

def get_pdv_db() -> object:
    if 'pdv_db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db() -> object:
    db = g.pop('pdv_db', None)
    if db is not None:
        db.close()

def get_products_by_description(db = object, query = str, params = str) -> list:
    rows = db.execute(query, [f'%{params}%']).fetchall()
    rows = [dict(row) for row in rows]

    prod = []
    insertIndex = 0
    for row in rows:
        des = row['description'][:len(params)]
        if des == params: 
            prod.insert(insertIndex, row)
            insertIndex += 1
        else: 
            prod.append(row) 

    return prod
