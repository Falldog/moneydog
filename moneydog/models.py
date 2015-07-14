from google.appengine.ext import ndb
from google.appengine.api import users


CATEGORY_IN = 1
CATEGORY_OUT = 2


def str2category(s):
    if s.upper() == 'IN':
        return CATEGORY_IN
    else:
        return CATEGORY_OUT

def category2str(c):
    if c == CATEGORY_IN:
        return 'IN'
    else:
        return 'OUT'


class TradeCategory(ndb.Model):
    user = ndb.UserProperty(required=True)
    c_type = ndb.IntegerProperty(required=True, choices=[CATEGORY_IN, CATEGORY_OUT])
    description = ndb.StringProperty(required=True)
    parent_key = ndb.KeyProperty(kind='TradeCategory', default=None)

    def delete(self):
        self.key.delete()

    @classmethod
    def query_by_c_type(cls, c_type):
        return cls.query().\
            filter(cls.user == users.get_current_user(), cls.c_type == c_type).\
            order(cls.description)
    @classmethod
    def query_in(cls):
        return cls.query_by_c_type(CATEGORY_IN)
    @classmethod
    def query_out(cls):
        return cls.query_by_c_type(CATEGORY_OUT)


class TradeItem(ndb.Model):
    user = ndb.UserProperty(required=True)
    c_type = ndb.IntegerProperty(required=True)
    category_key = ndb.KeyProperty(kind='TradeCategory')
    description = ndb.StringProperty(required=True)
    price = ndb.FloatProperty(required=True)
    date = ndb.DateProperty(required=True)

    def delete(self):
        self.key.delete()

    @classmethod
    def query_by_c_type(cls, c_type):
        return cls.query().filter(cls.user == users.get_current_user(), cls.c_type == c_type)
    @classmethod
    def query_in(cls):
        return cls.query_by_c_type(CATEGORY_IN)
    @classmethod
    def query_out(cls):
        return cls.query_by_c_type(CATEGORY_OUT)

