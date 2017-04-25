from behave import *
import server
from models import Product

def before_all(context):
    context.app = server.app.test_client()
    server.initialize_redis()
    Product.remove_all()
    context.server = server
    
def before_scenario(context, scenario):
    Product.remove_all()
    
def after_scenario(context, scenario): 
    Product.remove_all()
