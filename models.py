from flask import url_for
import pickle


######################################################################
# Product Model for database
#   This class must be initialized with use_db(redis) before using
#   where redis is a value connection to a Redis database
######################################################################
class Product(object):
    __redis = None

    def __init__(self, id=0, name=None, category=None, price=None, discontinued=False):
        self.id             = int(id)
        self.name           = name
        self.category       = category
        self.price          = price
        self.discontinued   = discontinued

    def discontinue(self):
        self.discontinued   = False

    def save(self):
        missing_attr        = None
        if not self.name:
            missing_attr    = 'name'
        if not self.category:
            missing_attr    = 'category'
        if not self.price:
            missing_attr    = 'price'
        if missing_attr:    
            raise AttributeError('%s attribute is not set' % (missing_attr))
        if self.id == 0:
            self.id         = self.__next_index()
        Product.__redis.set(self.id, pickle.dumps(self.serialize()))

    def delete(self):
        Product.__redis.delete(self.id)

    def __next_index(self):
        return Product.__redis.incr('index')

    def serialize(self):
        return {    "id":           self.id,        "name":     self.name, 
                    "category":     self.category,  "price":    self.price,
                    "discontinued": self.discontinued }

    def deserialize(self, data):
        try:
            self.name           = data['name']
            self.category       = data['category']
            self.price          = data['price']
            self.discontinued   = data.get('discontinued', False)
        except KeyError as e:
            raise DataValidationError('Invalid product: missing ' + e.args[0])
        except TypeError as e:
            raise DataValidationError('Invalid product: body of request contained bad or no data')
        return self

######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################
    @staticmethod
    def update_redis_store():
        """
        This is an update procedure to clean the Redis datastore.
        Initially data was stored as a dictionary - we need to remove
        old data types from the database
        """
        if 'newkey' in Product.__redis.keys():
            print 'Removing corrupted values'
            Product.remove_all()

    @staticmethod
    def use_db(redis):
        Product.__redis = redis
        

    @staticmethod
    def remove_all():
        Product.__redis.flushall()

    @staticmethod
    def all():
        results = []
        for key in Product.__redis.keys():
            if key != 'index':  # filer out our id index
                print str(key) + ' ' + str(type(key))
                data    = pickle.loads(Product.__redis.get(key))
                product = Product(data['id']).deserialize(data)
                results.append(product)
        return results

    @staticmethod
    def find(id):
        if Product.__redis.exists(id):
            data = pickle.loads(Product.__redis.get(id))
            product = Product(data['id']).deserialize(data)
            return product
        else:
            return None

    @staticmethod
    def find_or_404(id):
        product = Product.get(id)
        if not product:
            raise NotFound("Product with id '{}' was not found.".format(id))
        return product    