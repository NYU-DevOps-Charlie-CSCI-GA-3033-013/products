# run with:
# python -m unittest discover

import unittest
import json
import server
from models import Product

# Status Codes
HTTP_200_OK             = 200
HTTP_201_CREATED        = 201
HTTP_204_NO_CONTENT     = 204
HTTP_400_BAD_REQUEST    = 400
HTTP_404_NOT_FOUND      = 404
HTTP_409_CONFLICT       = 409

######################################################################
#  T E S T   C A S E S
######################################################################
class TestProductServer(unittest.TestCase):
    def setUp(self):
        server.app.debug = True
        self.app = server.app.test_client()
        server.initialize_redis()
        Product.remove_all()
        products = [ 
            Product(name='TV',        category='entertainment',   price=999, discontinued=True),
            Product(name='Blender',   category='appliances',      price =99, discontinued=False) ]
        for product in products:
            product.save()
    
    def tearDown(self):     
        Product.remove_all()      

    def test_index(self):
        resp = self.app.get('/')
        self.assertTrue ('product Demo REST API Service' in resp.data)
        self.assertTrue( resp.status_code == HTTP_200_OK )
    

    def test_get_product_list(self):
        resp = self.app.get('/products')
        self.assertTrue( resp.status_code == HTTP_200_OK )

        data = json.loads(resp.data)
        self.assertTrue( len(resp.data) > 0 ) 
        self.assertTrue(data[0]['name'] == 'TV')
        self.assertTrue(data[1]['name'] == 'Blender')

    def test_get_product_price(self):
        resp_min_price = self.app.get('/products?min-price=100')
        self.assertTrue( resp_min_price.status_code == HTTP_200_OK )
        data_min_price = json.loads(resp_min_price.data)
        self.assertTrue(data_min_price[0]['name'] == 'TV')
        self.assertEquals(len(data_min_price), 1)
        
        resp_max_price = self.app.get('/products?max-price=100')
        self.assertTrue( resp_max_price.status_code == HTTP_200_OK )
        data_max_price = json.loads(resp_max_price.data)
        self.assertTrue(data_max_price[0]['name'] == 'Blender')
        self.assertEquals(len(data_max_price), 1)
        
        resp_exact_price = self.app.get('/products?price=99')
        self.assertTrue( resp_exact_price.status_code == HTTP_200_OK )
        data_exact_price = json.loads(resp_exact_price.data)
        self.assertTrue(data_exact_price[0]['name'] == 'Blender')
        self.assertEquals(len(data_exact_price), 1)

    def test_get_product_limit(self):
        resp = self.app.get('/products?limit=1')
        self.assertTrue( resp.status_code == HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertTrue( len(data) == 1)
        
        resp = self.app.get('/products?limit=-1')
        self.assertTrue( resp.status_code == HTTP_400_BAD_REQUEST )

    def test_get_product_category(self):
        resp = self.app.get('/products?category=entertainment')
        self.assertTrue( resp.status_code == HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertTrue(data[0]['name'] == 'TV')
        self.assertTrue(len(data) == 1)

    def test_get_product(self):
        resp = self.app.get('/products/2')
        self.assertTrue( resp.status_code == HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertTrue (data['name'] == 'Blender')

    def test_query_product_list(self):
        self.assert_by__attribute('category',        'entertainment')
        self.assert_by__attribute('discontinued',    True)  
        self.assert_by__attribute('price',           999)
        self.assert_by__attribute('name',            'Blender')  

    def test_create_product(self):
        # save the current number of products for later comparison
        product_count = self.get_product_count()
        # add a new product
        new_product = {"name": "toaster", "category": "kitchen appliances", "price": 40}
        new_data    = json.dumps(new_product)
        resp        = self.app.post('/products', data=new_data, content_type='application/json')
        self.assertTrue( resp.status_code == HTTP_201_CREATED )
        new_json    = json.loads(resp.data)
        self.assertTrue(new_json['discontinued'] == False)
        self.assertEquals(self.get_product_count(), product_count+1)

    def test_update_product(self):
        new_blender = {"name": "Blender", "category": "home appliances", "discontinued": True, "price": 98}
        data = json.dumps(new_blender)
        resp = self.app.put('/products/2', data=data, content_type='application/json')
        self.assertTrue( resp.status_code == HTTP_200_OK )
        new_json = json.loads(resp.data)
        self.assertTrue (new_json['category']       == 'home appliances')
        self.assertTrue (new_json['discontinued']   == True)
        self.assertTrue (new_json['price']          == 98)
        
        resp = self.app.put('/products/5', data=data, content_type='application/json')
        self.assertTrue( resp.status_code == HTTP_404_NOT_FOUND )
    
    def test_discontinue_produce(self):
        resp = self.app.put('/products/2/discontinue')
        self.assertTrue( resp.status_code == HTTP_200_OK )
        new_json = json.loads(resp.data)
        self.assertTrue (new_json['discontinued']   == True)
        
        resp = self.app.put('/products/5/discontinue')
        self.assertTrue( resp.status_code == HTTP_404_NOT_FOUND )

    def test_update_product_with_no_name(self):
        new_product = {'category': 'entertainment'}
        data = json.dumps(new_product)
        resp = self.app.put('/products/2', data=data, content_type='application/json')
        self.assertTrue( resp.status_code == HTTP_400_BAD_REQUEST )

    def test_delete_product(self):
        # save the current number of products for later comparison
        product_count = self.get_product_count()
        # delete a product
        resp = self.app.delete('/products/2', content_type='application/json')
        self.assertTrue( resp.status_code == HTTP_204_NO_CONTENT )
        self.assertTrue( len(resp.data) == 0 )
        new_count = self.get_product_count()
        self.assertTrue ( new_count == product_count - 1)

    def test_create_product_with_no_name(self):
        new_product = {'category': 'entertainment'}
        data = json.dumps(new_product)
        resp = self.app.post('/products', data=data, content_type='application/json')
        self.assertTrue( resp.status_code == HTTP_400_BAD_REQUEST )

    def test_get_nonexisting_product(self):
        resp = self.app.get('/products/5')
        self.assertTrue( resp.status_code == HTTP_404_NOT_FOUND )

######################################################################
# Utility functions
######################################################################

    def get_product_count(self):
        # save the current number of products
        resp = self.app.get('/products')
        self.assertTrue( resp.status_code == HTTP_200_OK )
        data = json.loads(resp.data)
        return len(data)

    def assert_by__attribute(self, attr_name, attr_value):
        resp = self.app.get('/products', query_string='%s=%s' % (attr_name, str(attr_value)))
        self.assertTrue( resp.status_code == HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertEquals(len(data), 1)
        self.assertTrue(data[0][attr_name] == attr_value) 
######################################################################
#   M A I N
######################################################################

if __name__ == '__main__':
    unittest.main()
