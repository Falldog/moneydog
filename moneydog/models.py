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

    def delete(self, **argd):
        self.key.delete(**argd)

    def refresh(self):
        """
        [Tricky] : after update data, redirect to list trade page will still display old data
                   try to get item again will flush it for display new data
        """
        ndb.Key(urlsafe=self.key.urlsafe()).get(use_datastore=True, force_writes=True, use_cache=False, use_memcache=False)

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

    def delete(self, **argd):
        self.key.delete(**argd)

    def refresh(self):
        """
        [Tricky] : after update data, redirect to list trade page will still display old data
                   try to get item again will flush it for display new data
        """
        ndb.Key(urlsafe=self.key.urlsafe()).get(use_datastore=True, force_writes=True, use_cache=False, use_memcache=False)

    @classmethod
    def query_by_c_type(cls, c_type):
        return cls.query().filter(cls.user == users.get_current_user(), cls.c_type == c_type)
    @classmethod
    def query_in(cls):
        return cls.query_by_c_type(CATEGORY_IN)
    @classmethod
    def query_out(cls):
        return cls.query_by_c_type(CATEGORY_OUT)

