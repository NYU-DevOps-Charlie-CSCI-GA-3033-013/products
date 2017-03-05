#! python2
#!C:\Python27\python.exe -u

import csv
import os
from threading import Lock
from flask import Flask, Response, jsonify, request, json

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK             = 200
HTTP_201_CREATED        = 201
HTTP_204_NO_CONTENT     = 204
HTTP_400_BAD_REQUEST    = 400
HTTP_404_NOT_FOUND      = 404
HTTP_409_CONFLICT       = 409

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
    category        = request.args.get('category')
    discontinued    = str2bool(request.args.get('discontinued'))
    min_price       = request.args.get('min-price')
    max_price       = request.args.get('max-price')
    price           = request.args.get('price')
    limit           = request.args.get('limit')
    results         = []
    count           = 0
    cutoff          = 2

    if (limit is not None and int(limit) >= 0):
        cutoff = int(limit)
    elif (limit is not None and int(limit) < 0):
        return reply(results, HTTP_400_BAD_REQUEST)

    for key, value in products.iteritems():
        if (count == cutoff):
            break
        if matches_clause(category,      value['category']) and \
           matches_clause(discontinued,  value['discontinued']) and \
           matches_price(min_price, max_price, price, int(value['price'])):
                results.append(products[key])
        count += 1

    return reply(results, HTTP_200_OK)

def matches_price(min_price, max_price, price, value):
    return ((min_price is None or int(min_price) <= value) and \
           (max_price is None or int(max_price) >= value) and \
           (price is None or int(price) == value))

def matches_clause(clause_value, item_value):
    return clause_value is None or clause_value == item_value 

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
        insertUpdateProdEntry(id, products, payload)
        message = products[id]
        rc = HTTP_201_CREATED
    else:
        message = { 'error' : 'Data is not valid' }
        rc = HTTP_400_BAD_REQUEST

    return reply(message, rc)

######################################################################
# UPDATE AN EXISTING product
######################################################################
######################################################################
# UPDATE AN EXISTING product - Discontinue action
######################################################################

@app.route('/products/<int:id>', methods=['PUT'])
def update_products(id):
    if products.has_key(id):
        payload = request.get_json()
        if is_valid(payload):
            insertUpdateProdEntry(id, products, payload)
            message = products[id]
            rc = HTTP_200_OK
        else:
            message = { 'error' : 'product data was not valid' }
            rc = HTTP_400_BAD_REQUEST
    else:
        message = { 'error' : 'product %s was not found' % id }
        rc = HTTP_404_NOT_FOUND

    return reply(message, rc)

@app.route('/products/<int:id>/discontinue', methods=['PUT'])
def discontinue_products(id):
    if products.has_key(id):
        products[id]['discontinued']    = True
        message                         = products[id]
        rc = HTTP_200_OK
    else:
        message                         = { 'error' : 'product %s was not found' % id }
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
        price = data['price']
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
            prod_data[int(row['id'])] = {   'id':int(row['id']), 'name':row['name'], 'category':row['category'], \
                                            'discontinued': row.get('discontinued', False), \
                                            'price': row['price']   }
    return prod_data

def insertUpdateProdEntry(product_id, products, json_payload):
    products[product_id] = {'id': product_id, 'name': json_payload['name'], 'category': json_payload['category']}
    products[product_id]['discontinued'] = json_payload.get('discontinued', False)
    products[product_id]['price'] = json_payload.get('price')
    
def str2bool(value):
  return None if value is None else value.lower() in ("yes", "true", "t", "1")
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
