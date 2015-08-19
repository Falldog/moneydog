from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import search


CATEGORY_IN = 1
CATEGORY_OUT = 2


def tokenize_partialword(phrase):
    a = []
    for word in phrase.split():
        j = 1
        while True:
            for i in range(len(word) - j + 1):
                a.append(word[i:i + j])
            if j == len(word):
                break
            j += 1
    return a

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

    def to_json(self):
        return {
            'c_type': category2str(self.c_type),
            'description': self.description,
            'key': self.key.urlsafe(),
            'parent_key': self.parent_key.urlsafe() if self.parent_key else None,
        }

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
    SEARCH_INDEX_KEY = 'trade'
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

    def put_update_index(self, create=False, **argd):
        ret = self.put(**argd)
        if not create:
            self.delete_search_index()
        self.create_search_index()
        return ret

    def create_search_index(self):
        index = search.Index(name=TradeItem.SEARCH_INDEX_KEY)

        # split every word for search in partial word
        # Ex: day => d, a, y, da, ay, day
        text = ','.join(tokenize_partialword(self.description))

        doc = search.Document(
            doc_id=self.key.urlsafe(),
            fields=[search.TextField(name='description', value=text)],
            language='zh',
        )

        # Index the document.
        try:
            index.put(doc)
        except search.PutError, e:
            result = e.results[0]
            if result.code == search.OperationResult.TRANSIENT_ERROR:
                # possibly retry indexing result.object_id
                print 'search.PutError!'
        except search.Error, e:
            # possibly log the failure
            print 'search.Fail'

    def delete_search_index(self):
        # Get the index.
        index = search.Index(name=TradeItem.SEARCH_INDEX_KEY)
        try:
            index.delete(self.key.urlsafe())
        except search.DeleteError:
            pass


