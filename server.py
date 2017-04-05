#! python2
#!C:\Python27\python.exe -u

import csv
import os
from redis import Redis
from redis.exceptions import ConnectionError
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
    # products_url = request.base_url + "products"
    return 'index.html'
    # return jsonify(name='product Demo REST API Service',
    #                version='1.0',
    #                url=products_url
    #                ), HTTP_200_OK

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
    cutoff          = 10

    if (limit is not None and int(limit) >= 0):
        cutoff = int(limit)
    elif (limit is not None and int(limit) < 0):
        return reply(results, HTTP_400_BAD_REQUEST)
        
    for key in redis.keys():
		if(key == 'newkey'):
			continue
		product = redis.hgetall(key)
		if(count == cutoff):
			break
		if matches_clause(category,      product.get('category')) and \
          matches_clause(discontinued, str2bool(product.get('discontinued'))) and \
          matches_price(min_price, max_price, price, int(product.get('price'))):
							results.append(product)
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
 message = []
 if redis.exists(id):
		message = redis.hgetall(id)
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
		#insertUpdateProdEntry(id, products, payload)
		redis.hset(id,'id',id)
		redis.hset(id,'price',payload['price'])
		redis.hset(id,'name',payload['name'])
		redis.hset(id,'category',payload['category'])
		redis.hset(id,'discontinued',payload['discontinued'] )
		message = { 'success' : 'Data is valid'}
		redis.hset('newkey','newkey',int(id)+1)
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
        payload = request.get_json()
        if is_valid(payload):
			redis.hset(id,'price',payload['price'])
			redis.hset(id,'name',payload['name'])
			redis.hset(id,'category',payload['category'])
			redis.hset(id,'discontinued',payload['discontinued'] )
			message = { 'success' : 'update done' }
			rc = HTTP_200_OK
        else:
            message = { 'error' : 'product data was not valid' }
            rc = HTTP_400_BAD_REQUEST

	return reply(message, rc)
######################################################################
# UPDATE AN EXISTING product - Discontinue action
######################################################################
@app.route('/products/<int:id>/discontinue', methods=['PUT'])
def discontinue_products(id):
	if redis.exists(id):
		redis.hset(id,'discontinued', 'True' )
		message = redis.hgetall(id)
		rc = HTTP_200_OK
	else:
		message                         = { 'error' : 'product %s was not found' % id }
		rc = HTTP_404_NOT_FOUND

	return reply( message, rc)

######################################################################
# DELETE A product
######################################################################
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_products(id):
	if redis.exists(id):
		redis.delete(id)
	return '', HTTP_204_NO_CONTENT

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def next_index():
    # return max(products.keys()) + 1
	return redis.hget('newkey','newkey')

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
    
def str2bool(value):
  return None if value is None else value.lower() in ("yes", "true", "t", "1")
  
######################################################################
# Connect to Redis and catch connection exceptions
######################################################################
def connect_to_redis(hostname, port, password):
    redis = Redis(host=hostname, port=port, password=password)
    try:
        redis.ping()
    except ConnectionError:
        redis = None
    return redis

######################################################################
# INITIALIZE Redis
# This method will work in the following conditions:
#   1) In Bluemix with Redis bound through VCAP_SERVICES
#   2) With Redis running on the local server as with Travis CI
#   3) With Redis --link ed in a Docker container called 'redis'
######################################################################
def inititalize_redis():
    global redis
    redis = None
    # Get the crdentials from the Bluemix environment
    if 'VCAP_SERVICES' in os.environ:
        app.logger.info("Using VCAP_SERVICES...")
        VCAP_SERVICES = os.environ['VCAP_SERVICES']
        services = json.loads(VCAP_SERVICES)
        creds = services['rediscloud'][0]['credentials']
        app.logger.info("Conecting to Redis on host %s port %s" % (creds['hostname'], creds['port']))
        redis = connect_to_redis(creds['hostname'], creds['port'], creds['password'])
    else:
        app.logger.info("VCAP_SERVICES not found, checking localhost for Redis")
        redis = connect_to_redis('127.0.0.1', 6379, None)
        if not redis:
            app.logger.info("No Redis on localhost, using: redis")
            redis = connect_to_redis('redis', 6379, None)
    if not redis:
        # if you end up here, redis instance is down.
        app.logger.error('*** FATAL ERROR: Could not connect to the Redis Service')
        exit(1)
######################################################################
#   M A I N
######################################################################
products = {}
if __name__ == "__main__":
	inititalize_redis()
	debug = (os.getenv('DEBUG', 'False') == 'True')
	port = os.getenv('PORT', '5000')
	if not redis.exists('newkey'):
		redis.hset('newkey','newkey',len(redis.keys())+1)
	app.run(host='0.0.0.0', port=int(port), debug=debug)
