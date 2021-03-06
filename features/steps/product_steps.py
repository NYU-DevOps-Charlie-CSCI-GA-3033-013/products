from behave import *
import json
import server
from models import Product

@given(u'the server is started')
def step_impl(context):
 context.app = server.app.test_client()
 context.server = server

@when(u'I visit the "home page"')
def step_impl(context):
    context.resp = context.app.get('/')

@then(u'I should see "{message}"')
def step_impl(context, message):
    assert message in context.resp.data

@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.data

@given(u'the following products')
def step_impl(context):
    for row in context.table:#By default all data is in Unicode strings
        product = Product(id            =    int(row['id']),  name =     row['name'], 
                          category      =    row['category'], price =    int(row['price']), 
                          discontinued  =    row['discontinued'] == u'True')
        product.save()

@when(u'I visit "{url}"')
def step_impl(context, url):
    context.resp = context.app.get(url)
    assert context.resp.status_code == 200

##### CRUD FUNCTIONS #####
@when(u'I post "{url}" with name "{name}", category "{category}", discontinued "{discontinued}", and price "{price}"')
def step_impl(context, url, name, category, discontinued, price):    
    post_data       = json.dumps({ "name" : name,  "category" : category, "discontinued": discontinued.lower() == "true",  "price" : int(price)})
    context.resp    = context.app.post(url, data=post_data, content_type='application/json')
    assert context.resp.status_code == 201

@when(u'I delete "{url}" with id "{id}"')
def step_impl(context, url, id):
    target_url = url + '/' + id
    context.resp = context.app.delete(target_url)
    assert context.resp.status_code == 204
    assert context.resp.data is ""

@when(u'I retrieve "{url}" with id "{id}"')
def step_impl(context, url, id):
    target_url = url + '/' + id
    context.resp = context.app.get(target_url)
    assert context.resp.status_code == 200

@when(u'I change "{key}" to "{value}"')
def step_impl(context, key, value):
    data = json.loads(context.resp.data)
    data[key] = value
    context.resp.data = json.dumps(data)

@when(u'I update "{url}" with id "{id}"')
def step_impl(context, url, id):
    target_url = url + '/' + id
    context.resp = context.app.put(target_url, data=context.resp.data, content_type='application/json')
    assert context.resp.status_code == 200

##### SEARCHING FOR PRODUCTS ######

@when(u'I search "{url}" with minprice "{minprice}" and maxprice "{maxprice}"')
def step_imp(context, url, minprice, maxprice):
    target_url = url + "?min-price="+ minprice + "&max-price=" + maxprice 
    context.resp = context.app.get(target_url)
    assert context.resp.status_code == 200

@when(u'I search "{url}" with price "{price}"')
def step_imp(context, url, price):
    target_url = url + "?price="+ price 
    context.resp = context.app.get(target_url)
    assert context.resp.status_code == 200

@when(u'I search "{url}" with category "{category}"')
def step_imp(context, url, category):
    target_url = url + "?category="+ category 
    context.resp = context.app.get(target_url)
    assert context.resp.status_code == 200

@when(u'I search "{url}" with name "{name}"')
def step_imp(context, url, name):
    target_url = url + "?name="+ name 
    context.resp = context.app.get(target_url)
    assert context.resp.status_code == 200

@when(u'I search "{url}" with discontinued "{discontinued_status}"')
def step_imp(context, url, discontinued_status):
    target_url = url + "?discontinued="+ discontinued_status
    context.resp = context.app.get(target_url)
    assert context.resp.status_code == 200
