#! python2
#!C:\Python27\python.exe -u

import csv
import os
from redis import Redis
from redis.exceptions import ConnectionError
from threading import Lock
from flask import Flask, Response, request, json
from flasgger import Swagger
from models import Product

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK             = 200
HTTP_201_CREATED        = 201
HTTP_204_NO_CONTENT     = 204
HTTP_400_BAD_REQUEST    = 400
HTTP_404_NOT_FOUND      = 404
HTTP_409_CONFLICT       = 409


# Configure Swagger before initilaizing it
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "specs": [
        {
            "version": "1.0.0",
            "title": "DevOps Swagger Product App",
            "description": "This is Product store server.",
            "endpoint": 'v1_spec',
            "route": '/v1/spec'
        }
    ]
}

# Initialize Swagger after configuring it
Swagger(app)
######################################################################
# ERROR Handling
######################################################################

@app.errorhandler(ValueError)
def request_validation_error(e):
    return bad_request(e)

@app.errorhandler(400)
def bad_request(e):
    return reply({ "status":400, "error":'Bad Request', "message": e.message}, HTTP_400_BAD_REQUEST)

# Lock for thread-safe counter increment
lock = Lock()

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    return app.send_static_file('index.html')
    
######################################################################
# LIST ALL products
######################################################################
@app.route('/products', methods=['GET'])
def list_products():
    """
    Retrieve a list of Products
    This endpoint will return all Producst unless a query parameter is specificed
    ---
    tags:
      - Products
    description: The Products endpoint allows you to query Products
    parameters:
      - name: category
        in: query
        description: the category of Product you are looking for
        required: false
        type: string
      - name: name
        in: query
        description: the name of Product you are looking for
        required: false
        type: string
      - name: price
        in: query
        description: the price of Product you are looking for
        required: false
        type: string
      - name: limit
        in: query
        description: the number of Product entries you want
        required: false
        type: string
      - name: min-price
        in: query
        description: the minimum price of Product you are looking for
        required: false
        type: string
      - name: max-price
        in: query
        description: the maximum price of Product entries you want
        required: false
        type: string
    responses:
      200:
        description: An array of Products
        schema:
          type: array
          items:
            schema:
              id: Product
              properties:
                id:
                  type: integer
                  description: unique id assigned internally by service
                name:
                  type: string
                  description: the product's name
                category:
                  type: string
                  description: the category of product
                price:
                  type: string
                  description: the product's price
                discontinued:
                  type: string
                  description: the status of product
    """
    name = request.args.get('name')
    if name:
      name = name.lower()
    category = request.args.get('category')
    if category:
      category = category.lower()
    discontinued = str2bool(request.args.get('discontinued'))
    min_price = request.args.get('min-price')
    max_price = request.args.get('max-price')
    price = request.args.get('price')
    print 'price is',price
    limit = request.args.get('limit')
    products        = []
    count           = 0
    cutoff          = 10
    if (limit is not None and int(limit) >= 0):
       cutoff = int(limit)
    elif (limit is not None and int(limit) < 0):
       return reply(products, HTTP_400_BAD_REQUEST)
    for product in Product.all(): 
        if(count == cutoff):
           break
        print name,product.name.lower(),category,product.category.lower(),discontinued, product.discontinued,min_price, max_price, price, product.price

        if matches_clause(name,product.name.lower()) and matches_clause(category,product.category.lower()) and matches_clause(discontinued, product.discontinued) and matches_price(min_price, max_price, price, product.price):
              products.append(product)
              count = count + 1
    results = [product.serialize() for product in products]
    return reply(results, HTTP_200_OK)

def matches_clause(clause_value, item_value):
    return clause_value is None or clause_value == item_value

def matches_price(min_price, max_price, price, value):
    return ((min_price is None or int(min_price) <= int(value)) and (max_price is None or int(max_price) >= int(value)) and (price is None or int(price) == int(value)))

######################################################################
# RETRIEVE A product
######################################################################
@app.route('/products/<int:id>', methods=['GET'])
def get_products(id):
    """
    Retrieve a single Product
    This endpoint will return a Product based on its id
    ---
    tags:
      - Products
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of product to retrieve
        type: integer
        required: true
    responses:
      200:
        description: Product returned
        schema:
          id: Product
          properties:
            id:
              type: integer
              description: unique id assigned internally by service
            name:
              type: string
              description: the product's name
            category:
              type: string
              description: the category of product
            price:
              type: string
              description: the product's price
            discontinued:
              type: string
              description: the status of product
      404:
        description: Product not found
    """
    product = Product.find(id)
    if product:
        message = product.serialize()
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'Product with id: %s was not found' % str(id) }
        rc = HTTP_404_NOT_FOUND
    return reply(message, rc)    

######################################################################
# ADD A NEW product
######################################################################
@app.route('/products', methods=['POST'])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based on the data in the body that is posted
    ---
    tags:
      - Products
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: data
          required:
            - name
            - category
            - price
            - discontinued
          properties:
            name:
              type: string
              description: name for the Product
            category:
              type: string
              description: the category of product
            price:
              type: string
              description: price for the Product
            discontinued:
              type: string
              description: the status of product
    responses:
      201:
        description: Product created
        schema:
          id: Product
          properties:
            id:
              type: integer
              description: unique id assigned internally by service
            name:
              type: string
              description: the products's name
            category:
              type: string
              description: the category of product
            price:
              type: string
              description: the product's price
            discontinued:
              type: string
              description: the status of product
      400:
        description: Bad Request (the posted data was not valid)
    """
    data    = request.get_json()
    product = Product()
    product.deserialize(data)
    product.save()
    message = product.serialize()
    return reply(message, HTTP_201_CREATED)

######################################################################
# UPDATE AN EXISTING product
######################################################################
@app.route('/products/<int:id>', methods=['PUT'])
def update_products(id):
    """
    Update a Product
    This endpoint will update a Product based on the body that is posted
    ---
    tags:
      - Products
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of product to retrieve
        type: integer
        required: true
      - in: body
        name: body
        schema:
          id: data
          required:
            - name
            - category
            - price
            - discontinued
          properties:
            name:
              type: string
              description: name for the Product
            category:
              type: string
              description: the category of product
            price:
              type: string
              description: price of the Product
            discontinued:
              type: string
              description: the status of product
    responses:
      200:
        description: Product Updated
        schema:
          id: Product
          properties:
            id:
              type: integer
              description: unique id assigned internally by service
            name:
              type: string
              description: the products's name
            category:
              type: string
              description: the category of product
            price:
              type: string
              description: the products's price
            discontinued:
              type: string
              description: the status of product
      400:
        description: Bad Request (the posted data was not valid)
    """
    product     = Product.find(id)
    if product:
        product.deserialize(request.get_json())
        product.save()
        message = product.serialize()
        rc      = HTTP_200_OK
    else:
        message = { 'error' : 'Product with id: %s was not found' % id }
        rc      = HTTP_404_NOT_FOUND
    return reply(message, rc)

######################################################################
# UPDATE AN EXISTING product - Discontinue action
######################################################################
@app.route('/products/<int:id>/discontinue', methods=['PUT'])
def discontinue_products(id):
    """
    Discontinue a single Product
    This endpoint will discontinue a Product based on its id
    ---
    tags:
      - Products
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of product to discontinue
        type: integer
        required: true
    responses:
      200:
        description: Product discontinued
        schema:
          id: Product
          properties:
            id:
              type: integer
              description: unique id assigned internally by service
            name:
              type: string
              description: the product's name
            category:
              type: string
              description: the category of product
            price:
              type: string
              description: the product's price
            discontinued:
              type: string
              description: the status of product
      404:
        description: Product not found
    """
    product     = Product.find(id)
    if product:
        product.discontinue()
        product.save()
        message = product.serialize()
        rc      = HTTP_200_OK
    else:
        message = { 'error' : 'Product with id: %s was not found' % id }
        rc = HTTP_404_NOT_FOUND
    return reply(message, rc)

######################################################################
# DELETE A product
######################################################################
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_products(id):
    """
    Delete a Product
    This endpoint will delete a Product based on the id specified in the path
    ---
    tags:
      - Products
    description: Deletes a Product from the database
    parameters:
      - name: id
        in: path
        description: ID of product to delete
        type: integer
        required: true
    responses:
      204:
        description: Product deleted
    """
    product = Product.find(id)
    if product:
        product.delete()
    return reply('', HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def reply(message, rc):
    response = Response(json.dumps(message))
    response.headers['Content-Type'] = 'application/json'
    response.status_code = rc
    return response
    
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
#   3) With Redis --linked in a Docker container called 'redis'
######################################################################
def initialize_redis():
    global redis
    redis = None
    # Get the crdentials from the Bluemix environment
    if 'VCAP_SERVICES' in os.environ:
        app.logger.info("Using VCAP_SERVICES...")
        VCAP_SERVICES   = os.environ['VCAP_SERVICES']
        services        = json.loads(VCAP_SERVICES)
        creds           = services['rediscloud'][0]['credentials']
        app.logger.info("Conecting to Redis on host %s port %s" % (creds['hostname'], creds['port']))
        redis           = connect_to_redis(creds['hostname'], creds['port'], creds['password'])
    else:
        app.logger.info("VCAP_SERVICES not found, checking localhost for Redis")
        redis           = connect_to_redis('127.0.0.1', 6379, None)
        if not redis:
            app.logger.info("No Redis on localhost, using: redis")
            redis       = connect_to_redis('redis', 6379, None)
    if not redis:
        # if you end up here, redis instance is down.
        app.logger.error('*** FATAL ERROR: Could not connect to the Redis Service')
        exit(1)
    Product.use_db(redis)
    
######################################################################
#   M A I N
######################################################################
products = {}
if __name__ == "__main__":
    initialize_redis()
    debug  = (os.getenv('DEBUG', 'False') == 'True')
    port   = os.getenv('PORT', '5000')
    app.run(host='0.0.0.0', port=int(port), debug=debug)
