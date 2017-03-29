# run with:
# python -m unittest discover
# nosetests --exe -v --rednose --nologcapture

import unittest
import json
import server

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
        server.products = { 1: {'id':           1,      'name':     'TV',               'category':     'entertainment', 
                                'discontinued': True,   'price':    999,                'description':  'Flat Screen LCD'}, 
                           2: {'id':            2,      'name':     'Electric Blender', 'category':     'kitchen appliances', 
                               'discontinued': False,   'price':    99,                 'description' : 'European-made immersion blender'} 
                           }   

    def test_index(self):
        resp = self.app.get('/')
        self.assertIn ('product Demo REST API Service', resp.data)
        self.assertEqual(resp.status_code, HTTP_200_OK, 'Status should be HTTP_200_OK')

    def test_get_product_list(self):
        resp = self.app.get('/products')
        self.assertEqual(resp.status_code, HTTP_200_OK, 'Status should be HTTP_200_OK' )

        data = json.loads(resp.data)
        self.assertTrue( len(resp.data) > 0 ) 
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[1]['id'], 2)

    def test_get_product_price(self):
        resp_min_price = self.app.get('/products?min-price=100')
        self.assertEqual(resp_min_price.status_code, HTTP_200_OK)
        data_min_price = json.loads(resp_min_price.data)
        self.assert_single_value_by_id(data_min_price, 1)
        
        resp_max_price = self.app.get('/products?max-price=100')
        self.assertTrue( resp_max_price.status_code == HTTP_200_OK )
        data_max_price = json.loads(resp_max_price.data)
        self.assert_single_value_by_id(data_max_price, 2)

    def test_get_product_limit(self):
        valid_limit_resp = self.app.get('/products?limit=1')
        self.assertEqual(valid_limit_resp.status_code, HTTP_200_OK)
        data = json.loads(valid_limit_resp.data)
        self.assertEqual(len(data), 1)
        
        invalid_limit_resp = self.app.get('/products?limit=-1')
        self.assertEqual(invalid_limit_resp.status_code, HTTP_400_BAD_REQUEST)

    def test_get_product_category(self):
        resp = self.app.get('/products?category=entertainment')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = json.loads(resp.data)
        self.assert_single_value_by_id(data, 1)
        
    def test_get_product_search(self):
        search_by_name_resp = self.app.get('/products?search=blender')
        self.assertEqual(search_by_name_resp.status_code, HTTP_200_OK)
        data                = json.loads(search_by_name_resp.data)
        self.assert_single_value_by_id(data, 2)
        
        search_by_category_resp = self.app.get('/products?search=kitchen')
        self.assertTrue( search_by_category_resp.status_code == HTTP_200_OK )
        data                    = json.loads(search_by_category_resp.data)
        self.assert_single_value_by_id(data, 2)
        
        search_by_descrip_resp  = self.app.get('/products?search=Immersion')
        self.assertTrue( search_by_descrip_resp.status_code == HTTP_200_OK )
        data                    = json.loads(search_by_descrip_resp.data)
        self.assert_single_value_by_id(data, 2)
    

    def test_get_product(self):
        resp = self.app.get('/products/2')
        self.assertTrue( resp.status_code == HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertEqual(data['id'],  2)

    def test_query_product_list(self):
        self.setup_test_by_attribute('category',        'entertainment')
        self.setup_test_by_attribute('discontinued',    True)  
        self.setup_test_by_attribute('price',           999)  

    def test_create_product(self):
        # save the current number of products for later comparison
        product_count   = self.get_product_count()
        # add a new product
        new_product     = {'name': 'toaster', 'category': 'kitchen appliances', 'price': 99}
        data            = json.dumps(new_product)
        resp            = self.app.post('/products', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        new_json        = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'toaster')
        # check default value of 'discontinued' is 'False'
        self.assertEqual(new_json['discontinued'], False)
        # check the price of the product
        self.assertEqual(new_json['price'], 99)
        # check that count has gone up
        resp = self.app.get('/products?limit=' + str(product_count + 1))
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code,  HTTP_200_OK)
        self.assertEqual(len(data),         product_count + 1 )
        self.assertIn( new_json, data )

    def test_update_product(self):
        test_product_id             = 2
        test_name                   = 'Immersion Blender'
        test_category               = 'home appliances'
        test_discontinued_status    = True
        test_price                  = 50
        test_description            = 'This is a test description'
        update_prod = { 'id':           test_product_id,            'name':     test_name,  'category':     test_category, 
                        'discontinued': test_discontinued_status,   'price':    test_price, 'description':  test_description }
        data = json.dumps(update_prod)
        resp = self.app.put('/products/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK )
        new_json = json.loads(resp.data)
        self.assertEqual(sorted(new_json.items()), sorted(update_prod.items()))
        #Attempt to update a record whose ID is not found
        unfound_product_id  = 999
        update_prod['id']     = unfound_product_id
        data = json.dumps(update_prod)
        resp = self.app.put('/products/'+str(unfound_product_id), data=data, content_type='application/json')
        self.assertEqual(resp.status_code,  HTTP_404_NOT_FOUND)
    
    def test_discontinue_produce(self):
        resp = self.app.put('/products/2/discontinue')
        self.assertEqual(resp.status_code,          HTTP_200_OK )
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['discontinued'],  True)#fixme - Reset this
        
        unfound_product_id  = 999
        resp = self.app.put('/products/%d/discontinue' % (unfound_product_id))
        self.assertEqual(resp.status_code,  HTTP_404_NOT_FOUND)

    def test_update_product_with_no_name(self):
        new_product = {'category': 'entertainment'}
        data = json.dumps(new_product)
        resp = self.app.put('/products/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST )

    def test_delete_product(self):
        # save the current number of products for later comparrison
        product_count = self.get_product_count()
        # delete a product
        resp        = self.app.delete('/products/2', content_type='application/json')
        self.assertEqual(resp.status_code,  HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data),    0 )
        new_count   = self.get_product_count()
        self.assertEqual(new_count, product_count - 1)

    def test_create_product_with_no_name(self):
        new_product = {'category': 'entertainment'}
        data = json.dumps(new_product)
        resp = self.app.post('/products', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_get_nonexisting_product(self):
        resp = self.app.get('/products/5')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

######################################################################
# Utility functions
######################################################################

    def get_product_count(self):
        # save the current number of products
        resp = self.app.get('/products')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        # print 'resp_data: ' + resp.data
        data = json.loads(resp.data)
        return len(data)

    def setup_test_by_attribute(self, attr_name, attr_value):
        resp        = self.app.get('/products', \
                            query_string='attr_name=attr_value'.format(attr_name=attr_name, attr_value=attr_value))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue( len(resp.data) > 0 )
        data        = json.loads(resp.data)
        query_item  = data[0]
        self.assertEqual(query_item[attr_name], attr_value) 
        
    def assert_single_value_by_id(self, prod_test_data, prod_id):
        self.assertEqual(len(prod_test_data),       1, 'data must be only single value')
        self.assertEqual(prod_test_data[0]['id'],   prod_id)    
######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
