from behave import *
import server

def before_all(context):
    context.app = server.app.test_client()
    server.initialize_redis()
    context.server = server
