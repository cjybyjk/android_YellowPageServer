#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import lookup

from contextlib import closing
from flask import Flask, request, abort, g, jsonify
from datachecker import check_type, check_region

app = Flask(__name__)
app.config.from_json('settings.json')

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read().decode('utf-8'))
        db.commit()

def is_protected_number(number, region):
    cursor = g.db.execute('select * from protected_number where number = ? and region = ?', (number, region))
    return cursor.rowcount > 0

def report_number(number, region, number_type, tagstr, tag_count = 1):
    if (is_protected_number(number, region)):
        return create_response_dict(1, 'number protected')
    
    g.db.execute('insert or ignore into tag_data VALUES (?, ?, ?, ?, ?)', (number, region, number_type, tagstr, 0))
    g.db.execute('update tag_data set tag_count = tag_count + ? where number = ? and region = ?', (tag_count, number, region))
    g.db.commit()

    return create_response_dict(0, 'ok')

def query_number(number, region):
    if is_protected_number(number, region):
        return create_response_dict(2, 'number protected')

    cursor = g.db.execute('select * from tag_data where number = ? and region = ?', (number, region))
    result = cursor.fetchone()
    if result is not None and result[4] > 3: # This record is valid if more than 3 users have tagged it 
        return create_response_dict(0, 'ok', {
            'number': result[0],
            'region': result[1],
            'type': result[2],
            'tagstr': result[3],
            'tag_count': result[4]
        })
    else:
        lookups = (lookup.SogouLookup(), lookup.BaiduLookup())
        for l in lookups:
            if l.is_supported_region(region):
                res = l.query(number, region)
                if res is not None:
                    report_number(number, region, res['type'], res['tagstr'], 4)
                    return create_response_dict(0, 'ok', res)

    return create_response_dict(1, 'not found')

@app.before_request
def before_request():
    g.db = connect_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

def create_response_dict(code, msg, data = None):
    ret = {'status': code, 
           'msg': msg}
    if data is not None:
        ret['data'] = data
    return ret

@app.route('/query', methods=['GET'])
def query():
    if 'number' in request.args:
        number = request.args['number']
        if number.isdigit():
            region = request.args.get('region', app.config['DEFAULT_REGION'])
            if not check_region(region): 
                region = app.config['DEFAULT_REGION']
            
            return jsonify(query_number(request.args['number'], region))

    abort(400)

@app.route('/report', methods=['GET', 'POST'])
def report():
    data = None
    if request.method == 'GET':
        data = request.args
    else:
        data = request.form
    
    if 'number' in data and 'type' in data and 'region' in data and 'tagstr' in data:
        number = data['number']
        if number.isdigit() and check_type(data['type']) and check_region(data['region']):
            return jsonify(report_number(number, data['region'], data['type'], data['tagstr']))

    abort(400)

if __name__ == '__main__':
    init_db()
    if app.config.get('USE_SSL'):
        app.run(debug=False, port=app.config.get('PORT'), ssl_context=(app.config.get('SSL_CERT'), app.config.get('SSL_KEY')))
    else:
        app.run(debug=False, port=app.config.get('PORT'))       
