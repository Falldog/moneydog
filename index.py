#!/usr/bin/env python
# -*- coding=utf-8

import cgi
import datetime
import wsgiref.handlers
import os
import time
import re
import string

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from django.utils import simplejson as json

from lib import gmemsess
from util import *

CATEGORY_IN  = db.Category('in')
CATEGORY_OUT = db.Category('out')

# DataStore
#-------------------------------------------------------------------------------------------------------------------------------------------
class TradeCategory( db.Model ):
    user        = db.UserProperty()
    type        = db.CategoryProperty()
    description = db.StringProperty(multiline=True)
  
  
class TradeItem( db.Model ):
    user        = db.UserProperty()
    category    = db.ReferenceProperty( TradeCategory )
    type        = db.CategoryProperty()
    description = db.StringProperty(multiline=True)
    price       = db.IntegerProperty()
    date        = db.DateProperty()


#-------------------------------------------------------------------------------------------------------------------------------------------
def GetCategory():
    result = TradeCategory.gql( "Where user=:1 AND type=:2 ORDER BY description", users.get_current_user(), 'in' )
    in_items = []
    for i in result :
        item = {}
        item['key'] = i.key()
        item['description'] = i.description
        in_items.append( item )
    
    result = TradeCategory.gql( "Where user=:1 AND type=:2 ORDER BY description", users.get_current_user(), 'out' )
    out_items = []
    for i in result :
        item = {}
        item['key'] = i.key()
        item['description'] = i.description
        out_items.append( item )
    
    return ( in_items, out_items )

#-------------------------------------------------------------------------------------------------------------------------------------------
class MainPage( webapp.RequestHandler ):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write( template.render( path, None ))
    
    
class Login( webapp.RequestHandler ):
    def get(self):
        sess=gmemsess.Session(self)
        if( sess.is_new() ):
            # not yet login!
            user = users.get_current_user()
            if user:
                sess['moneydog_name'] = user.nickname()
                sess.save()
            else :
                self.redirect(users.create_login_url(self.request.uri))
                return
        self.redirect("list_aj")
    
class Logout( webapp.RequestHandler ):
    def get(self):
        sess=gmemsess.Session(self)
        if( not sess.is_new() ):
            sess.invalidate()
        self.redirect( users.create_logout_url(self.request.uri) )
  
  
class ListAdd( webapp.RequestHandler ):
    def get(self):
        type = self.request.get('type')
        
        if type==None:
            self.add_list_out()
        elif type=='in':
            self.add_list_in()
        elif type=='out':
            self.add_list_out()
        elif type=='category_in':
            self.add_list_category_in()
        elif type=='category_out':
            self.add_list_category_out()
        
    def add_list_in(self):
        trade = TradeItem()
        trade.user        = users.get_current_user()
        trade.price       = int( self.request.get('item_price') )
        trade.description = self.request.get('item_description')
        trade.category    = db.get( self.request.get('item_category_id') )
        trade.type        = CATEGORY_IN
    
        add_date = datetime.datetime.strptime( self.request.get('item_date'), "%Y-%m-%d" )
        trade.date        = datetime.date( add_date.year, add_date.month, add_date.day )
        trade.put()
        trade.save()
        
        #self.redirect('/list?type=in')
    
    
    def add_list_out(self):
        trade = TradeItem()
        trade.user        = users.get_current_user()
        trade.price       = int( self.request.get('item_price') )
        trade.description = self.request.get('item_description')
        trade.category    = db.get( self.request.get('item_category_id') )
        trade.type        = CATEGORY_OUT
    
        add_date = datetime.datetime.strptime( self.request.get('item_date'), "%Y-%m-%d" )
        trade.date        = datetime.date( add_date.year, add_date.month, add_date.day )
        trade.put()
        trade.save()
        
        #self.redirect('/list?type=out')
    
    
    def add_list_category_in(self):
        category = TradeCategory()
        category.user = users.get_current_user()
        category.type = db.Category('in')
        category.description = self.request.get('item_description')
        category.put()
    
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write( 'add_list_category_in '  )
        #self.response.out.write( category.description )
        #self.redirect('/list?type=category_in')
    
    def add_list_category_out(self):
        category = TradeCategory()
        category.user = users.get_current_user()
        category.type = 'out'
        category.description = self.request.get('item_description')
        category.put()
    
        #self.redirect('/list?type=category_out')
    
class ListEdit( webapp.RequestHandler ):
    def get(self):
        type = self.request.get('type')
        do   = self.request.get('do')
        if do=='aj':
            if( type=='in' or type=='out' ):
                item = db.get( db.Key( self.request.get('edit_key') ) )
                item.category    = db.get( self.request.get('edit_category') )
                item.price       = int( self.request.get('edit_price') )
                item.description = self.request.get('edit_description')
                add_date         = datetime.datetime.strptime( self.request.get('edit_time'), "%Y-%m-%d" )
                item.date        = datetime.date( add_date.year, add_date.month, add_date.day )
                item.put()
                item.save()
                
            elif( type=='category_in' or type=='category_out' ):
                item = db.get( db.Key( self.request.get('edit_key') ) )
                item.description = self.request.get('edit_description')
                item.put()
            #self.redirect('/list?type='+type)

class ListDelete( webapp.RequestHandler ):
    def get(self):
        type = self.request.get('type')
        item = db.get( db.Key( self.request.get('item_key') ) )
        if item:
            if type=='category_in' or type=='category_out':
                query = TradeItem.gql( "WHERE user=:1 AND category=:2 ", users.get_current_user(), item )
                result = query.fetch(1)
                if result: 
                    self.response.headers['Content-Type'] = 'text/plain'
                    self.response.out.write('尚有資料使用此分類...無法刪除!!!')
                    return
                else: 
                    item.delete()
            else:
                item.delete()
        #self.redirect('/list?type='+type)

class Search( webapp.RequestHandler ):
    def get(self):
        ''' Search TradeItem in the Description '''
        type = 'search_result'#self.request.get('type')
        
        words = self.request.get('key_words')
        words = words.lower()
        query = TradeItem.gql( "Where user=:1", users.get_current_user() )
        
        my_offset = 500
        cur_offset= 0
        
        items = []
        msg = {}
        msg['price_max'] = 0
        msg['price_total'] = 0
        
        result = query.fetch( limit=500, offset=cur_offset )
        while result :
            for i in result :
                # Find the keyword in the description~
                if string.find( i.description.lower(), words ) >=0 :
                    item = {
                        'key'         : str(i.key()),
                        'price'       : i.price,
                        'category'    : i.category.description,
                        'description' : i.description,
                        'date'        : str(i.date),
                    }
                    item['type'] = 'in' if i.type == CATEGORY_IN else 'out'
                    items.append( item )
                    
                    msg['price_max'] = max( msg['price_max'], i.price )
                    msg['price_total'] += i.price
            
            cur_offset += my_offset
            result = query.fetch( limit=500, offset=cur_offset )
        
        self.response.out.write( json.dumps(items) )
    
    
class SearchCategory( webapp.RequestHandler ):
    def get(self):
        ''' Search TradeItem in the Description '''
        type = 'search_result'#self.request.get('type')
        
        cate_desc = self.request.get('category')
        #print words.encode('utf-8')
        query_cate = TradeCategory.gql( "Where user=:1 AND description=:2 ", users.get_current_user(), cate_desc )
        result = query_cate.fetch(1)
        if not result:
            self.response.out.write('')
            return
        cate = result[0]
        query = TradeItem.gql( "Where user=:1 AND category=:2", users.get_current_user(), cate )
        
        my_offset = 500
        cur_offset= 0
        
        items = []
        msg = {}
        msg['price_max'] = 0
        msg['price_total'] = 0
        
        result = query.fetch( limit=500, offset=cur_offset )
        while result :
            for i in result :
                # Find the keyword in the description~
                if string.find( i.category.description, cate_desc ) >=0 :
                    item = {
                        'key'         : str(i.key()),
                        'price'       : i.price,
                        'category'    : i.category.description,
                        'description' : i.description,
                        'date'        : str(i.date),
                    }
                    item['type'] = 'in' if i.type == CATEGORY_IN else 'out'
                    items.append( item )
                    
                    msg['price_max'] = max( msg['price_max'], i.price )
                    msg['price_total'] += i.price
            
            cur_offset += my_offset
            result = query.fetch( limit=500, offset=cur_offset )
        
        self.response.out.write( json.dumps(items) )


class Test( webapp.RequestHandler ):
    def post(self):
        self.get()
    
    def get(self):
        print users.get_current_user().nickname()
        print users.get_current_user()

    
class ListAjax( webapp.RequestHandler ):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/list_aj.html')
        self.response.out.write( template.render( path, None ))


class Query( webapp.RequestHandler ):
    def _outputItemsByJson(self, items):
        self.response.out.write( json.dumps(items) )
      
    def post(self):
        self.get()
        
    def get(self):
        type = self.request.get('type')
        
        if type==None or type=="":
            type = 'out'
            self.do_query_out()
        elif type=='in':
            self.do_query_in()
        elif type=='out':
            self.do_query_out()
        elif type=='category_in':
            self.do_query_category_in();
        elif type=='category_out':
            self.do_query_category_out()
        elif type=='search_category':
            self.do_search_category()
        elif type=='user_name':
            self.do_query_user_name()
            
    def do_query_in(self):
        try:
            year =  int( self.request.get('year') )
            month = int( self.request.get('month') )
        except ValueError:
            year  = 0
            month = 0
        if year==None or year==0:     year = datetime.datetime.now().year
        if month==None or month==0:   month = datetime.datetime.now().month
        dt = datetime.datetime(year,month,1)
        
        query = TradeItem.gql( "WHERE user=:1 AND type=:2 AND date>=:3 AND date<=:4 ORDER BY date", 
                               users.get_current_user(), 
                               CATEGORY_IN, 
                               datetime.datetime(year,month,1), 
                               datetime.datetime(year,month,LastDayOfMonth(dt)) )
        items = []
        for i in query :
            item = {
                'key'         : str(i.key()),
                'price'       : i.price,
                'category'    : i.category.description,
                'description' : i.description,
                'date'        : str(i.date),
            }
            items.append( item )
            
        self._outputItemsByJson(items)
        
    def do_query_out(self):
        try:
            year =  int( self.request.get('year') )
            month = int( self.request.get('month') )
        except ValueError:
            year  = 0
            month = 0
        if year==None or year==0:     year = datetime.datetime.now().year
        if month==None or month==0:   month = datetime.datetime.now().month
        dt = datetime.datetime(year,month,1)
    
        query = TradeItem.gql( "WHERE user=:1 AND type=:2 AND date>=:3 AND date<=:4 ORDER BY date, description", 
                               users.get_current_user(), 
                               CATEGORY_OUT, 
                               datetime.datetime(year,month,1), 
                               datetime.datetime(year,month,LastDayOfMonth(dt)) )
        items = []
        pre_item = {}
        for i in query:
            item = {
                'key'         : str(i.key()),
                'price'       : i.price,
                'category'    : i.category.description,
                'description' : i.description,
                'date'        : str(i.date),
            }
            items.append( item )
            
        self._outputItemsByJson(items)
        
    def do_query_category_in(self):
        result = TradeCategory.gql( "Where user=:1 AND type=:2", 
                                    users.get_current_user(), 
                                    db.Category('in') )
        items = []
        for i in result:
            item = {
                'key'         : str(i.key()),
                'user'        : i.user.nickname(),
                'description' : i.description,
            }
            items.append( item )
        
        items.sort(key=lambda x:x['description'])
        self._outputItemsByJson(items)
            
    def do_query_category_out(self):
        result = TradeCategory.gql( "Where user=:1 AND type=:2", 
                                    users.get_current_user(), 
                                    'out' )
        items = []
        for i in result :
            item = {
                'key'         : str(i.key()),
                'user'        : i.user.nickname(),
                'description' : i.description,
            }
            items.append( item )
        
        items.sort(key=lambda x:x['description'])
        self._outputItemsByJson(items)
      
    def do_query_user_name(self):
        self.response.out.write( users.get_current_user().nickname() )


application = webapp.WSGIApplication([
        ('/',      MainPage),
        ('/index', MainPage),
        ('/login', Login),
        ('/logout',Logout),  
        ('/list_add',  ListAdd),
        ('/list_edit', ListEdit),
        ('/list_delete', ListDelete),
        ('/search', Search),
        ('/searchCate', SearchCategory),
        ('/test', Test),
        ('/query', Query),
        ('/list_aj', ListAjax),
    ], debug=True)

application_login = webapp.WSGIApplication([
  ('/login', Login),
  ('/.*', MainPage),
], debug=True)


def main():
    if users.get_current_user() == None :
        wsgiref.handlers.CGIHandler().run( application_login )
    else :
        wsgiref.handlers.CGIHandler().run( application )


if __name__ == '__main__':
  main()
