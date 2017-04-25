# Test cases can be run with either of the following:
# python -m unittest discover
# nosetests -v --rednose --nologcapture

import unittest
import json
from redis import Redis
from werkzeug.exceptions import NotFound
from models import Product
import server  # to get Redis

######################################################################
#  T E S T   C A S E S
######################################################################
class TestProducts(unittest.TestCase):

    def setUp(self):
        server.initialize_redis()
        Product.use_db(server.redis)
        # Product.use_db(Redis(host='127.0.0.1', port=6379))
        Product.remove_all()
    
    def tearDown(self):     
        Product.remove_all()      

    def test_create_a_product(self):
        # Create a product and assert that it exists
        product = Product(id=0, name="TV", category="entertainment", price=500)
        self.assertNotEqual(    product,                None )
        self.assertEqual(       product.id,             0 )
        self.assertEqual(       product.name,           "TV" )
        self.assertEqual(       product.category,       "entertainment" )
        self.assertEqual(       product.price,           500 )
        self.assertEqual(       product.discontinued,   False )
    
    def test_discontinue_product(self):
        product = Product(id=0, name="TV",        category="entertainment",   price=500)
        self.assertEqual(       product.discontinued,   False )
        product.discontinue()
        self.assertEqual(       product.discontinued,   True )

    def test_add_a_product(self):
        # Create a product and add it to the database
        products = Product.all()
        self.assertEqual( products, [])
        product = Product(id=0, name="TV", category="entertainment", price=500)
        self.assertTrue( product != None )
        self.assertEqual( product.id, 0 )
        product.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual( product.id, 1 )
        products = Product.all()
        self.assertEqual( len(products), 1)
        self.assertEqual( products[0].id, 1 )
        self.assertEqual( products[0].name, "TV" )
        self.assertEqual( products[0].category, "entertainment" )
        self.assertEqual( products[0].discontinued, False )

    def test_update_a_product(self):
        product = Product(id=0, name="TV", category="entertainment", price=500)
        product.save()
        self.assertEqual( product.id, 1 )
        # Change it an save it
        product.category = "electronics"
        product.save()
        self.assertEqual( product.id, 1 )
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual( len(products), 1)
        self.assertEqual( products[0].category, "electronics")
        self.assertEqual( products[0].name, "TV" )

    def test_delete_a_product(self):
        product = Product(id=0, name="TV", category="entertainment", price=500)
        product.save()
        self.assertEqual( len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual( len(Product.all()), 0)

    def test_serialize_a_product(self):
        product = Product(id=0, name="TV", category="entertainment", price=500)
        data = product.serialize()
        self.assertNotEqual( data, None )
        self.assertIn( 'id', data )
        self.assertEqual( data['id'], 0 )
        self.assertIn( 'name', data )
        self.assertEqual( data['name'], "TV" )
        self.assertIn( 'category', data )
        self.assertEqual( data['category'], "entertainment" )
        self.assertIn( 'price', data )
        self.assertEqual( data['price'], 500 )
        self.assertIn( 'discontinued', data )
        self.assertEqual( data['discontinued'], False )

    def test_deserialize_a_product(self):
        data = {"id":1, "name": "Blender", "category": "appliances", "discontinued": True, "price": 500 }
        product = Product(data['id'])
        product.deserialize(data)
        self.assertNotEqual( product,           None )
        self.assertEqual( product.id,           1 )
        self.assertEqual( product.name,         "Blender" )
        self.assertEqual( product.category,     "appliances" )
        self.assertEqual( product.price,        500 )
        self.assertEqual( product.discontinued, True )

    def test_deserialize_a_product_with_no_name(self):
        data = {"id":0, "category": "appliances", "price": 500}
        product = Product(0)
        self.assertRaises(ValueError, product.deserialize, data)

    def test_deserialize_a_product_with_no_data(self):
        product = Product(0)
        self.assertRaises(ValueError, product.deserialize, None)

    def test_deserialize_a_product_with_bad_data(self):
        product = Product(0)
        self.assertRaises(ValueError, product.deserialize, "string data")

    def test_save_a_product_with_no_name(self):
        product = Product(id=0, category="entertainment", price=500)
        self.assertRaises(AttributeError, product.save)

    def test_find_product(self):
        Product(id=0, name="TV",        category="entertainment",   price=500).save()
        Product(id=0, name="Blender",   category="appliances",      price=100).save()
        product = Product.find(2)
        self.assertIsNot( product, None)
        self.assertEqual( product.id, 2 )
        self.assertEqual( product.name, "Blender" )

    def test_find_with_no_products(self):
        product = Product.find(1)
        self.assertIs( product, None)

    def test_product_not_found(self):
        Product(id=0, name="TV", category="entertainment", price=500).save()
        product = Product.find(2)
        self.assertIs( product, None)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestProducts)
    # unittest.TextTestRunner(verbosity=2).run(suite)
