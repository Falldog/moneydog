from flask import request
from flask import render_template
from flask import abort, redirect, url_for

from google.appengine.api import users
from google.appengine.ext import ndb

from moneydog import app
from moneydog.models import TradeCategory, TradeItem, CATEGORY_IN, CATEGORY_OUT, str2category, category2str
from moneydog.lib.decorators import login_required, update_basic_context

import calendar
from datetime import date


@login_required
@update_basic_context
def index():
    #return "Fucking all Hello world!!!"
    return render_template('index.html', testing="Fucking all")

#def login():
#    pass

def _get_category_items(c_type):
    items = []
    q = TradeCategory.query_by_c_type(str2category(c_type))
    for d in q.fetch():
        items.append(d)
    return items


@login_required
@update_basic_context
def list_trade(c_type):
    year = int(request.args.get('year', '0'))
    month = int(request.args.get('month', '0'))
    if year == 0:
        year = date.today().year
    if month == 0:
        month = date.today().month
    mdays = calendar.monthrange(year, month)[1]

    q = TradeItem.query_by_c_type(str2category(c_type))
    q = q.filter(TradeItem.date >= date(year, month, 1))
    q = q.filter(TradeItem.date <= date(year, month, mdays))
    q = q.order(TradeItem.date, TradeItem.description)

    items = [d for d in q.fetch()]

    context = {
        "c_type": c_type,
        "items": items,
        "year": year,
        "month": month,
        "category_items": _get_category_items(c_type),
    }
    return render_template('list_trade.html', **context)


@login_required
@update_basic_context
def edit_trade(url_key):
    item = ndb.Key(urlsafe=url_key).get()
    assert isinstance(item, TradeItem)

    if request.method == "GET":
        context = {
            "item": item,
            "c_type": category2str(item.c_type),
            "category_items": [d for d in TradeCategory.query_by_c_type(item.c_type).fetch()],
        }
        print 'fuck0'
        for i in context['category_items']:
            if i.key == item.category_key:
                print 'fuck1'
            #if i.description == item.category.description:
            #    print 'fuck2'
        return render_template('edit_trade.html', **context)

    else:  # POST => update
        category_key = request.form['category']
        item.category_key = ndb.Key(urlsafe=category_key)
        item.price = float(request.form['price'])
        item.description = request.form['description']
        item.put(use_datastore=True, force_writes=True, use_cache=False, use_memcache=False)

        # [Tricky] : after update data, redirect to list trade page will still display old data
        #            try to get item again will flush it for display new data
        ndb.Key(urlsafe=item.key.urlsafe()).get()

        return redirect('/list/trade/%s?year=%s&month=%s' % (category2str(item.c_type), item.date.year, item.date.month))


@login_required
@update_basic_context
def remove_trade(url_key):
    item = ndb.Key(urlsafe=url_key).get()
    assert isinstance(item, TradeItem)
    item.delete()

    return redirect('/list/trade/'+category2str(item.c_type))

@login_required
@update_basic_context
def list_category(c_type):
    items = []
    q = TradeCategory.query_by_c_type(str2category(c_type))
    for d in q.fetch():
        items.append(d)

    context = {
        "category_items": items,
    }
    return render_template('list_category.html', **context)


@login_required
@update_basic_context
def edit_category(url_key):
    item = ndb.Key(urlsafe=url_key).get()
    assert isinstance(item, TradeCategory)

    if request.method == "GET":
        context = {
            "item": item,
            "c_type": category2str(item.c_type),
            "category_items": [d for d in TradeCategory.query_by_c_type(item.c_type).fetch()],
        }
        return render_template('edit_category.html', **context)

    else:  # POST => update
        parent_category = request.form['parent_category']
        if parent_category:
            parent_category = ndb.Key(urlsafe=parent_category).get()

        item.description = request.form['description']
        item.parent_key = parent_category.key if parent_category else None
        item.put()

        return redirect('/list/category/'+category2str(item.c_type))


@login_required
@update_basic_context
def remove_category(url_key):
    item = ndb.Key(urlsafe=url_key).get()
    assert isinstance(item, TradeCategory)

    # reset the parent_key set on the category which ready to remove
    q = TradeCategory.query().filter(TradeCategory.parent_key == item.key)
    for d in q.fetch():
        d.parent_key = None
        d.put()

    item.delete()

    return redirect('/list/category/'+category2str(item.c_type))


@login_required
@update_basic_context
def add_category():
    if request.method == "GET":
        return render_template('add_category.html')

    else:
        t = TradeCategory(
            user = users.get_current_user(),
            description=request.form['description'],
            c_type=str2category(request.form['category']),
        )
        t.put()
        return redirect(url_for('index'))


