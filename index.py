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

MAX_FETCH_LIMIT = 1000

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
    result = TradeCategory.gql( "Where user=:1 AND type=:2 ORDER BY description", users.get_current_user(), CATEGORY_IN )
    in_items = []
    for i in result :
        item = {}
        item['key'] = i.key()
        item['description'] = i.description
        in_items.append( item )
    
    result = TradeCategory.gql( "Where user=:1 AND type=:2 ORDER BY description", users.get_current_user(), CATEGORY_OUT )
    out_items = []
    for i in result :
        item = {}
        item['key'] = i.key()
        item['description'] = i.description
        out_items.append( item )
    
    return ( in_items, out_items )

#-------------------------------------------------------------------------------------------------------------------------------------------
class CacheCmdBase(object):
    def ResponseInJson(self, cmd, data):
        data = {'cmd':cmd, 'data':data}
        self.response.out.write( json.dumps(data) )
        
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
        
        if type is None:
            self.add_list_trade(CATEGORY_OUT)
        elif type=='in':
            self.add_list_trade(CATEGORY_IN)
        elif type=='out':
            self.add_list_trade(CATEGORY_OUT)
        elif type=='category_in':
            self.add_list_category(CATEGORY_IN)
        elif type=='category_out':
            self.add_list_category(CATEGORY_OUT)
        
    def add_list_trade(self, category):
        trade = TradeItem()
        trade.user        = users.get_current_user()
        trade.price       = int( self.request.get('item_price') )
        trade.description = self.request.get('item_description')
        trade.category    = db.get( self.request.get('item_category_id') )
        trade.type        = category
    
        add_date = datetime.datetime.strptime( self.request.get('item_date'), "%Y-%m-%d" )
        trade.date        = datetime.date( add_date.year, add_date.month, add_date.day )
        trade.put()
        trade.save()
        
    def add_list_category(self, cate):
        category = TradeCategory()
        category.user = users.get_current_user()
        category.type = cate
        category.description = self.request.get('item_description')
        category.put()
        
    
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

class Search( webapp.RequestHandler, CacheCmdBase ):
    def get(self):
        ''' Search TradeItem in the Description '''
        
        key_words = self.request.get('key_words')
        words = key_words.lower()
        query = TradeItem.gql( "Where user=:1", users.get_current_user() )
        
        offset= 0
        
        items = []
        msg = {}
        msg['price_max'] = 0
        msg['price_total'] = 0
        
        while True:
            result = query.fetch( limit=MAX_FETCH_LIMIT, offset=offset )
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
            
            if len(result) < MAX_FETCH_LIMIT:
                break
            offset += MAX_FETCH_LIMIT
        
        cmd = {'cmd':'search',
               'key_words':key_words }
        self.ResponseInJson(cmd, items)
    
    
class SearchCategory( webapp.RequestHandler, CacheCmdBase ):
    def get(self):
        ''' Search TradeItem in the Description '''
        
        cate_desc = self.request.get('category')
        cate_type = self.request.get('type')
        _summary = cate_type.startswith('summary')
        _type = CATEGORY_IN if cate_type.split('_')[1] == 'in' else CATEGORY_OUT
        
        #print words.encode('utf-8')
        query_cate = TradeCategory.gql( "Where user=:1 AND description=:2 AND type=:3 ", 
                                        users.get_current_user(), 
                                        cate_desc,
                                        _type )
        result = query_cate.fetch(1)
        if not result:
            self.response.out.write('')
            return
        cate = result[0]
        
        if _summary:
            year = int(self.request.get('year'))
            dt_begin = datetime.datetime(year,1,1)
            dt_end = datetime.datetime(year,12,31)
            query = TradeItem.gql( "Where user=:1 AND category=:2 AND date>=:3 AND date<=:4 ORDER BY date, description", 
                                            users.get_current_user(), 
                                            cate,
                                            dt_begin,
                                            dt_end )
        else:
            query = TradeItem.gql( "Where user=:1 AND category=:2 ORDER BY date DESC, description", users.get_current_user(), cate )
        
        offset= 0
        
        items = []
        msg = {}
        msg['price_max'] = 0
        msg['price_total'] = 0
        
        while True:
            result = query.fetch( limit=MAX_FETCH_LIMIT, offset=offset )
            for i in result :
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
                
            if len(result) < MAX_FETCH_LIMIT:
                break
            offset += MAX_FETCH_LIMIT
        
        cmd = {'cmd':'searchCate',
               'type':cate_type,
               'category':cate_desc }
        self.ResponseInJson(cmd, items)


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


class Query( webapp.RequestHandler, CacheCmdBase ):
    def post(self):
        self.get()
        
    def get(self):
        type = self.request.get('type')
        
        if type==None or type=="":
            type = 'out'
            self.do_query_trade(CATEGORY_OUT)
        elif type=='in':
            self.do_query_trade(CATEGORY_IN)
        elif type=='out':
            self.do_query_trade(CATEGORY_OUT)
        elif type=='category_in':
            self.do_query_category(CATEGORY_IN)
        elif type=='category_out':
            self.do_query_category(CATEGORY_OUT)
        elif type=='user_name':
            self.do_query_user_name()
        elif type=='valid_year':
            self.do_query_valid_year()
        elif type=='summary_out':
            self.do_query_summary(CATEGORY_OUT)
        elif type=='summary_in':
            self.do_query_summary(CATEGORY_IN)
            
    def do_query_trade(self, category=CATEGORY_OUT):
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
                               category, 
                               datetime.datetime(year,month,1), 
                               datetime.datetime(year,month,LastDayOfMonth(dt)) )
        items = []
        for i in query:
            item = {
                'key'         : str(i.key()),
                'price'       : i.price,
                'category'    : i.category.description,
                'description' : i.description,
                'date'        : str(i.date),
            }
            items.append( item )
            
        cmd = {'cmd':'query',
               'type':category,
               'year':year,
               'month':month }
        self.ResponseInJson(cmd, items)
        
    def do_query_category(self, category=CATEGORY_OUT):
        result = TradeCategory.gql( "Where user=:1 AND type=:2", 
                                    users.get_current_user(), 
                                    category )
        items = []
        for i in result :
            item = {
                'key'         : str(i.key()),
                'user'        : i.user.nickname(),
                'description' : i.description,
            }
            items.append( item )
        
        items.sort(key=lambda x:x['description'])
        
        str_category = 'category_' + category
        cmd = {'cmd':'query',
               'type':str_category}
        self.ResponseInJson(cmd, items)
    
    def do_query_summary(self, category=CATEGORY_OUT):
        try:
            year =  int( self.request.get('year') )
        except ValueError:
            year = datetime.datetime.now().year
        
        query = TradeItem.gql( "WHERE user=:1 AND type=:2 AND date>=:3 AND date<=:4", 
                               users.get_current_user(),
                               category,
                               datetime.datetime(year,1,1),
                               datetime.datetime(year,12,31) )
        
        # query all items of the year
        items = []
        offset = 0
        while True:
            result = query.fetch( limit=MAX_FETCH_LIMIT, offset=offset )
            items.extend(result)
            if len(result) < MAX_FETCH_LIMIT:
                break
            offset += MAX_FETCH_LIMIT
        
        #separate the items by month
        summary = [[] for i in range(12)]
        for i in items:
            item = {
                'key'         : str(i.key()),
                'price'       : i.price,
                'category'    : i.category.description,
            }
            m = i.date.month-1
            summary[m].append(item)
        
        _type = 'summary_in' if category is CATEGORY_IN else 'summary_out'
        cmd = {'cmd':'query',
               'type':_type,
               'year':year }
        self.ResponseInJson(cmd, summary)
    
    def do_query_user_name(self):
        self.response.out.write( users.get_current_user().nickname() )
    
    def do_query_valid_year(self):
        query = TradeItem.gql( "WHERE user=:1 ORDER BY date", 
                               users.get_current_user() )
        item = query.get()
        
        cur_year = datetime.datetime.now().year
        if item is None:
            year = cur_year
        else:
            year = item.date.year
        
        valid = (cur_year, year) if year > cur_year else (year, cur_year)
        
        cmd = {'cmd':'query',
               'type':'valid_year'}
        self.ResponseInJson(cmd, valid)
        
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
