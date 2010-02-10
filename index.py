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

#import mylib.gmemsess
from mylib import search
from mylib import gmemsess
from my_func import *

CATEGORY_IN  = db.Category('in')
CATEGORY_OUT = db.Category('out')

LINE_SEP = '$\n'
SEP      = '$#'


# DataStore
#-------------------------------------------------------------------------------------------------------------------------------------------
class TradeCategory( db.Model ):
    user        = db.UserProperty()
    type        = db.CategoryProperty()
    description = db.StringProperty(multiline=True)
  
  
class TradeItem(search.SearchableModel):
    user        = db.UserProperty()
    category    = db.ReferenceProperty( TradeCategory )
    type        = db.CategoryProperty()
    description = db.StringProperty(multiline=True)
    price       = db.IntegerProperty()
    date        = db.DateProperty()


#-------------------------------------------------------------------------------------------------------------------------------------------
def GetCategory():

    # query = db.Query( TradeCategory )
    # query.filter( 'user=', users.get_current_user() )
    # query.filter( 'type=', 'in' )
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

    # category_values = {
      # 'category_in': in_items,
      # 'category_out': out_items
    # }
    return ( in_items, out_items )

def GetOtherPorperty( template_values, year, month ):
    #Add Time : Year & Month
    template_values['year']  = year
    template_values['month'] = month
    template_values['list_year'] = range( year-4, year+5 )
    template_values['list_month'] = range( 1, 13 )
    if month==12 :
        template_values['year_n'] = year+1
        template_values['year_p'] = year
        template_values['month_n'] = 1
        template_values['month_p'] = month-1
    elif month==1 :
        template_values['year_n'] = year
        template_values['year_p'] = year-1
        template_values['month_n'] = month+1
        template_values['month_p'] = 12
    else:
        template_values['year_n'] = year
        template_values['year_p'] = year
        template_values['month_n'] = month+1
        template_values['month_p'] = month-1

def _cmp_func(x,y):
    return cmp(x[1],y[1])
    
def DoStatistics( values ):
    if values['items'] is None:
        values['stat'] = []
        return
        
    result = {}
    for i in values['items']:
        if result.get( i['category'] ) is None :
            result[ i['category'] ] = 0
        result[ i['category'] ] += i['_price']
    result = result.items()
    result.sort( cmp=_cmp_func )
    values['stat'] = [ {'category':k[0], 'price':IntAddComma(k[1])} for k in result ]
    values['stat'].reverse()
    idx = 1
    for i in values['stat']:
        i['index'] = idx
        idx += 1

    
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
  
  
  
class List( webapp.RequestHandler ):
  def post(self):
    get()
    
  def get(self):
    #self.response.headers['Content-Type'] = 'text/plain'
    #self.response.out.write('List!')
    type = self.request.get('type')
    
    if( type==None or type=="" ):
        type = 'out'
        self.do_list_out()
    elif( type=='in' ):
        self.do_list_in()
    elif( type=='out' ):
        self.do_list_out()
    elif( type=='category_in' ):
        self.do_list_category_in();
    elif( type=='category_out' ):
        self.do_list_category_out()
    elif( type=='search_category' ):
        self.do_search_category()
    
  def do_list_in(self):
  
    #result = TradeItem.gql( "Where user=:1", users.get_current_user() )
    try:
        year =  int( self.request.get('year') )
        month = int( self.request.get('month') )
    except ValueError:
        year  = 0
        month = 0
    if year==None or year==0:     year = datetime.datetime.now().year
    if month==None or month==0:   month = datetime.datetime.now().month
    dt = datetime.datetime(year,month,1)
    
    #query = TradeItem.gql( "WHERE user=:1 AND type=:2 AND date>=:3 AND date<=:4 ", users.get_current_user(), CATEGORY_IN, datetime.datetime(year,month,1), datetime.datetime(year,month,31) )
    query = TradeItem.gql( "WHERE user=:1 AND type=:2 AND date>=:3 AND date<=:4 ORDER BY date", users.get_current_user(), CATEGORY_IN, datetime.datetime(year,month,1), datetime.datetime(year,month,LastDayOfMonth(dt)) )
    items = []
    msg = {}
    msg['price_max'] = 0
    msg['price_total'] = 0
    for i in query :
        item = {}
        item['key'] = i.key()
        item['price'] = IntAddComma(i.price)
        item['category'] = i.category.description
        item['description'] = i.description
        item['date'] = i.date
        items.append( item )
        
        msg['price_max'] = max( msg['price_max'], i.price )
        msg['price_total'] += i.price
        
        
    (category_in,category_out) = GetCategory()
    template_values = {
      'type': 'in',
      'show_type': 'trade',
      'category_in' : category_in,
      'category_out': category_out,
      'items': items,
      'user': users.get_current_user(),
      'msg' : msg,
    }
    GetOtherPorperty( template_values, year, month )    
    
    path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
    self.response.out.write( template.render( path, template_values ))

  def do_list_out(self):

    try:
        year =  int( self.request.get('year') )
        month = int( self.request.get('month') )
    except ValueError:
        year  = 0
        month = 0
    if year==None or year==0:     year = datetime.datetime.now().year
    if month==None or month==0:   month = datetime.datetime.now().month
    dt = datetime.datetime(year,month,1)

    query = TradeItem.gql( "WHERE user=:1 AND type=:2 AND date>=:3 AND date<=:4 ORDER BY date", users.get_current_user(), CATEGORY_OUT, datetime.datetime(year,month,1), datetime.datetime(year,month,LastDayOfMonth(dt)) )
    items = []
    pre_item = {}
    msg = {}
    msg['price_max'] = 0
    msg['price_total'] = 0
    for i in query :
        item = {}
        item['key'] = i.key()
        item['price'] = IntAddComma(i.price)
        item['_price'] = i.price
        item['_category'] = i.category
        item['category'] = i.category.description
        item['description'] = i.description
        item['date'] = i.date
        
        #日期不一樣 則插入一空白行 support by New Version...
        #if pre_item!={}  and  pre_item['date']!=item['date']: items.append({});
        #pre_item = item
        
        items.append( item )
        
        msg['price_max'] = max( msg['price_max'], i.price )
        msg['price_total'] += i.price
        
        

    (category_in,category_out) = GetCategory()
    template_values = {
      'type': 'out',
      'show_type': 'trade',
      'category_in' : category_in,
      'category_out': category_out,
      'items':        items,
      'user': users.get_current_user(),
      'msg' : msg,
    }
    GetOtherPorperty( template_values, year, month )
    DoStatistics( template_values )
    
    path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
    self.response.out.write( template.render( path, template_values ))
    
    
  def do_list_category_in(self):
    result = TradeCategory.gql( "Where user=:1 AND type=:2", users.get_current_user(), db.Category('in') )
    items = []
    for i in result :
        item = {}
        item['key'] = i.key()
        item['user'] = i.user.nickname()
        item['description'] = i.description
        items.append( item )

    template_values = {
      'type': 'category_in',
      'show_type': 'category',
      'items': items,
      'user': users.get_current_user()
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
    self.response.out.write( template.render( path, template_values ))
    
  def do_list_category_out(self):
    result = TradeCategory.gql( "Where user=:1 AND type=:2", users.get_current_user(), 'out' )
    items = []
    for i in result :
        item = {}
        item['key'] = i.key()
        item['user'] = i.user.nickname()
        item['description'] = i.description
        items.append( item )

    template_values = {
      'type': 'category_out',
      'show_type': 'category',
      'items': items,
      'user': users.get_current_user()
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
    self.response.out.write( template.render( path, template_values ))
    
  def do_search_category(self):
    cate = db.get( db.Key( self.request.get('category_key') ) )
    query = TradeItem.gql( "Where user=:1 AND category=:2", users.get_current_user(), cate )
    items = []
    msg = {}
    msg['price_max'] = 0
    msg['price_total'] = 0
    for i in query :
        item = {}
        item['key'] = i.key()
        item['price'] = IntAddComma(i.price)
        item['category'] = i.category.description
        item['description'] = i.description
        item['date'] = i.date
        if i.type == CATEGORY_IN :
            item['type'] = 'in'
            item['in_or_out'] = '收入'
        else :
            item['type'] = 'out'
            item['in_or_out'] = '支出'
        items.append( item )
        
        msg['price_max'] = max( msg['price_max'], i.price )
        msg['price_total'] += i.price

    (category_in,category_out) = GetCategory()
    template_values = {
      'type': 'search_category',
      'show_type': 'search_result',
      'category_in' : category_in,
      'category_out': category_out,
      'items':        items,
      'user':         users.get_current_user(),
      'msg':  msg,
    }
    
    path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
    self.response.out.write( template.render( path, template_values ))
    
    
    
class ListAdd( webapp.RequestHandler ):
  def get(self):
    type = self.request.get('type')
    
    if( type==None ):
        self.add_list_out()
    elif( type=='in' ):
        self.add_list_in()
    elif( type=='out' ):
        self.add_list_out()
    elif( type=='category_in' ):
        self.add_list_category_in();
    elif( type=='category_out' ):
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
    
    self.redirect('/list?type=in')
    
    
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
    
    self.redirect('/list?type=out')
    
    
  def add_list_category_in(self):
    template_values = {
      'type': 'category_in',
    }
    #category = TradeCategory( user= )
    category = TradeCategory()
    category.user = users.get_current_user()
    category.type = db.Category('in')
    category.description = self.request.get('item_description')
    category.put()

    #self.response.headers['Content-Type'] = 'text/plain'
    #self.response.out.write( 'add_list_category_in '  )
    #self.response.out.write( category.description )
    self.redirect('/list?type=category_in')
    
  def add_list_category_out(self):
    template_values = {
      'type': 'category_out',
    }
    category = TradeCategory()
    category.user = users.get_current_user()
    category.type = 'out'
    category.description = self.request.get('item_description')
    category.put()

    self.redirect('/list?type=category_out')
    
class ListEdit( webapp.RequestHandler ):
  def get(self):
    type = self.request.get('type')
    do   = self.request.get('do')
    if( do=='edit' ):
        item = db.get( db.Key( self.request.get('item_key') ) )
        if item:
            (category_in,category_out) = GetCategory()
            template_values = {
              'type': type,
              'category_in' : category_in,
              'category_out': category_out,
              'item': item
            }
            path = os.path.join(os.path.dirname(__file__), 'templates/list_edit.html')
            self.response.out.write( template.render( path, template_values ))
            
    elif do=='result':
        if( type=='in' or type=='out' ):
            item = db.get( db.Key( self.request.get('item_key') ) )
            item.category    = db.get( self.request.get('item_category_id') )
            item.price       = int( self.request.get('item_price') )
            item.description = self.request.get('item_description')    
            add_date         = datetime.datetime.strptime( self.request.get('item_date'), "%Y-%m-%d" )
            item.date        = datetime.date( add_date.year, add_date.month, add_date.day )
            item.put()
            item.save()
            
        elif( type=='category_in' or type=='category_out' ):
            item = db.get( db.Key( self.request.get('item_key') ) )
            item.description = self.request.get('item_description')
            item.put()
        self.redirect('/list?type='+type)
        
    elif do=='aj':
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
        self.redirect('/list?type='+type)

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
    self.redirect('/list?type='+type)

class Search( webapp.RequestHandler ):
  def get(self):
    ''' Search TradeItem in the Description '''
    type = 'search_result'#self.request.get('type')
    
    template_values = {}
    words = self.request.get('key_words')
    #query = TradeItem.all().search( words )
    #print words.encode('utf-8')
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
            if string.find( i.description, words ) >=0 :
                item = {}
                item['key'] = i.key()
                item['price'] = i.price
                item['category'] = i.category.description
                item['description'] = i.description
                item['date'] = i.date
                if i.type == CATEGORY_IN :
                    item['type'] = 'in'
                else : 
                    item['type'] = 'out'
                
                items.append( item )
                
                msg['price_max'] = max( msg['price_max'], i.price )
                msg['price_total'] += i.price
        
        cur_offset += my_offset
        result = query.fetch( limit=500, offset=cur_offset )
    
    html = ''
    for i in items:
        #html = '<tr> <td></td> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td> </tr>' % (i['date'], i['price'], i['category'], i['description'])
        html += '%s%s%s%s%s%s%s%s%s%s%s%s' % (i['type'], SEP, i['date'], SEP, i['price'], SEP, i['category'], SEP, i['description'], SEP, i['key'], LINE_SEP)
    self.response.out.write( html )
    
    
  def Old_get(self):
    ''' (Old Style... may not work.)Search TradeItem in the SearchDB '''
    type = self.request.get('type')
    
    template_values = {}
    words = self.request.get('key_words')
    query = TradeItem.all().search( words )
    
    items = []
    msg = {}
    msg['price_max'] = 0
    msg['price_total'] = 0
    for i in query :
        item = {}
        item['key'] = i.key()
        item['price'] = i.price
        item['category'] = i.category.description
        item['description'] = i.description
        item['date'] = i.date
        items.append( item )

        msg['price_max'] = max( msg['price_max'], i.price )
        msg['price_total'] += i.price
    (category_in,category_out) = GetCategory()
    template_values = {
      'type': type,
      'show_type': 'trade',
      'category_in' : category_in,
      'category_out': category_out,
      'items':items,
      'msg':msg
    }
        
    path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
    self.response.out.write( template.render( path, template_values ))  
    
    
    
class Test( webapp.RequestHandler ):
  def post(self):
    get(self)
    
  def get(self):
    print users.get_current_user().nickname()
    print users.get_current_user()

    
class ListAjax( webapp.RequestHandler ):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/list_aj.html')
    self.response.out.write( template.render( path, None ))

class Query( webapp.RequestHandler ):
  def post(self):
    get()
    
  def get(self):
    #self.response.headers['Content-Type'] = 'text/plain'
    #self.response.out.write('List!')
    type = self.request.get('type')
    
    if( type==None or type=="" ):
        type = 'out'
        self.do_query_out()
    elif( type=='in' ):
        self.do_query_in()
    elif( type=='out' ):
        self.do_query_out()
    elif( type=='category_in' ):
        self.do_query_category_in();
    elif( type=='category_out' ):
        self.do_query_category_out()
    elif( type=='search_category' ):
        self.do_search_category()
    elif( type=='user_name' ):
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
    
    #query = TradeItem.gql( "WHERE user=:1 AND type=:2 AND date>=:3 AND date<=:4 ", users.get_current_user(), CATEGORY_IN, datetime.datetime(year,month,1), datetime.datetime(year,month,31) )
    query = TradeItem.gql( "WHERE user=:1 AND type=:2 AND date>=:3 AND date<=:4 ORDER BY date", users.get_current_user(), CATEGORY_IN, datetime.datetime(year,month,1), datetime.datetime(year,month,LastDayOfMonth(dt)) )
    #query = TradeItem.gql( "WHERE user=:1 AND type=:2 ORDER BY date", users.get_current_user(), CATEGORY_IN )
    items = []
    for i in query :
        item = {}
        item['key'] = i.key()
        item['price'] = i.price
        item['category'] = i.category.description
        item['description'] = i.description
        item['date'] = i.date
        items.append( item )
        
    for i in items:
        #html = '<tr> <td></td> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td> </tr>' % (i['date'], i['price'], i['category'], i['description'])
        html = '%s%s%s%s%s%s%s%s%s%s' % (i['date'], SEP, i['price'], SEP, i['category'], SEP, i['description'], SEP, i['key'], LINE_SEP)
        self.response.out.write( html )
    
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

    query = TradeItem.gql( "WHERE user=:1 AND type=:2 AND date>=:3 AND date<=:4 ORDER BY date", users.get_current_user(), CATEGORY_OUT, datetime.datetime(year,month,1), datetime.datetime(year,month,LastDayOfMonth(dt)) )
    #query = TradeItem.gql( "WHERE user=:1 AND type=:2 ORDER BY date", users.get_current_user(), CATEGORY_OUT, )
    items = []
    pre_item = {}
    for i in query :
        item = {}
        item['key'] = i.key()
        item['price'] = i.price
        item['category'] = i.category.description
        item['description'] = i.description
        item['date'] = i.date
        
        items.append( item )
        
    LINE_SEP = '$\n'
    SEP      = '$#'
    for i in items:
        #html = '<tr> <td></td> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td> </tr>' % (i['date'], i['price'], i['category'], i['description'])
        html = '%s%s%s%s%s%s%s%s%s%s' % (i['date'], SEP, i['price'], SEP, i['category'], SEP, i['description'], SEP, i['key'], LINE_SEP)
        self.response.out.write( html )
        
  def do_query_category_in(self):
    result = TradeCategory.gql( "Where user=:1 AND type=:2", users.get_current_user(), db.Category('in') )
    items = []
    for i in result :
        item = {}
        item['key'] = i.key()
        item['user'] = i.user.nickname()
        item['description'] = i.description
        items.append( item )
    items.sort(key=lambda x:x['description'])
    
    template_values = {
      'type': 'category_in',
      'show_type': 'category',
      'items': items,
      'user': users.get_current_user()
    }
    
    #path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
    #self.response.out.write( template.render( path, template_values ))
    for i in items:
        html = '%s%s%s%s' % ( i['key'], SEP, i['description'], LINE_SEP )
        self.response.out.write( html )
        
  def do_query_category_out(self):
    result = TradeCategory.gql( "Where user=:1 AND type=:2", users.get_current_user(), 'out' )
    items = []
    for i in result :
        item = {}
        item['key'] = i.key()
        item['user'] = i.user.nickname()
        item['description'] = i.description
        items.append( item )
    items.sort(key=lambda x:x['description'])
    
    template_values = {
      'type': 'category_out',
      'show_type': 'category',
      'items': items,
      'user': users.get_current_user()
    }
    #path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
    #self.response.out.write( template.render( path, template_values ))
    for i in items:
        html = '%s%s%s%s' % ( i['key'], SEP, i['description'], LINE_SEP )
        self.response.out.write( html )
  
  def do_query_user_name(self):
    self.response.out.write( users.get_current_user().nickname() )
    
application = webapp.WSGIApplication([
  ('/',      MainPage),
  ('/index', MainPage),
  ('/login', Login),
  ('/logout',Logout),  
  ('/list',  List),
  ('/list_add',  ListAdd),
  ('/list_edit', ListEdit),
  ('/list_delete', ListDelete),
  ('/search', Search),
  ('/test', Test),
  ('/query', Query),
  ('/list_aj',  ListAjax),
], debug=True)

application_login = webapp.WSGIApplication([
  ('/login', Login),
  (r'/.*', MainPage),
], debug=True)

def main():
    if users.get_current_user() == None :
        wsgiref.handlers.CGIHandler().run( application_login )
    else :
        wsgiref.handlers.CGIHandler().run( application )


if __name__ == '__main__':
  main()
