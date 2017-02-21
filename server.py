#! python2
#!C:\Python27\python.exe -u

import csv
import os
from threading import Lock
from flask import Flask, Response, jsonify, request, json

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

# Lock for thread-safe counter increment
lock = Lock()

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    products_url = request.base_url + "products"
    return jsonify(name='product Demo REST API Service',
                   version='1.0',
                   url=products_url
                   ), HTTP_200_OK

######################################################################
# LIST ALL products
######################################################################
@app.route('/products', methods=['GET'])
def list_products():
    results = products.values()
    category = request.args.get('category')
    if category:
        results = []
        for key, value in products.iteritems():
            if value['category'] == category:
                results.append(products[key])

    return reply(results, HTTP_200_OK)

######################################################################
# RETRIEVE A product
######################################################################
@app.route('/products/<int:id>', methods=['GET'])
def get_products(id):
    if products.has_key(id):
        message = products[id]
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'product with id: %s was not found' % str(id) }
        rc = HTTP_404_NOT_FOUND

    return reply(message, rc)

######################################################################
# ADD A NEW product
######################################################################
@app.route('/products', methods=['POST'])
def create_products():
    payload = request.get_json()
    if is_valid(payload):
        id = next_index()
        products[id] = {'id': id, 'name': payload['name'], 'category': payload['category']}
        message = products[id]
        rc = HTTP_201_CREATED
    else:
        message = { 'error' : 'Data is not valid' }
        rc = HTTP_400_BAD_REQUEST

    return reply(message, rc)

######################################################################
# UPDATE AN EXISTING product
######################################################################
@app.route('/products/<int:id>', methods=['PUT'])
def update_products(id):
    if products.has_key(id):
        payload = request.get_json()
        if is_valid(payload):
            products[id] = {'id': id, 'name': payload['name'], 'category': payload['category']}
            message = products[id]
            rc = HTTP_200_OK
        else:
            message = { 'error' : 'product data was not valid' }
            rc = HTTP_400_BAD_REQUEST
    else:
        message = { 'error' : 'product %s was not found' % id }
        rc = HTTP_404_NOT_FOUND

    return reply(message, rc)

######################################################################
# DELETE A product
######################################################################
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_products(id):
    del products[id];
    return '', HTTP_204_NO_CONTENT

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def next_index():
    return max(products.keys()) + 1

def reply(message, rc):
    response = Response(json.dumps(message))
    response.headers['Content-Type'] = 'application/json'
    response.status_code = rc
    return response

def is_valid(data):
    valid = False
    try:
        name = data['name']
        category = data['category']
        valid = True
    except KeyError as err:
        app.logger.error('Missing parameter error: %s', err)
    return valid

PRODUCTS_DATA_SOURCE_FILE = 'sampleSchema_products.csv'
def get_product_data():
    prod_data = {}
    with open(PRODUCTS_DATA_SOURCE_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            prod_data[int(row['id'])] = { 'id':int(row['id']), 'name':row['name'], 'category':row['category']   }
    return prod_data

######################################################################
#   M A I N
######################################################################
products = {}
if __name__ == "__main__":
    products = get_product_data();
    # Pull options from environment
    debug = (os.getenv('DEBUG', 'False') == 'True')
    port = os.getenv('PORT', '5000')
    app.run(host='0.0.0.0', port=int(port), debug=debug)
