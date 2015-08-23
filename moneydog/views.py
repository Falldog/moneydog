from flask import request
from flask import render_template
from flask import abort, redirect, url_for
from flask import jsonify

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import search

from moneydog import app
from moneydog.models import TradeCategory, TradeItem, CATEGORY_IN, CATEGORY_OUT, str2category, category2str
from moneydog.lib.decorators import login_required, update_basic_context
from moneydog.lib.util import str2date

import calendar
from datetime import date


@login_required
@update_basic_context
def index():
    return render_template('index.html', testing="Fucking all")


def _get_category_items(c_type):
    if isinstance(c_type, basestring):
        c_type = str2category(c_type)
    items = []
    q = TradeCategory.query_by_c_type(c_type)
    for d in q.fetch():
        items.append(d)
    return items

# ========================================== TradeItem ==========================================

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
        "is_basic_list": True,
        "items": items,
        "year": year,
        "month": month,
        "category_items": _get_category_items(c_type),
    }
    return render_template('list_trade.html', **context)


@login_required
@update_basic_context
def list_trade_by_category(url_key):
    c = ndb.Key(urlsafe=url_key).get()
    assert isinstance(c, TradeCategory)

    q = TradeItem.query_by_c_type(c.c_type)
    q = q.filter(TradeItem.category_key == c.key)
    q = q.order(TradeItem.date, TradeItem.description)

    items = [d for d in q.fetch()]

    context = {
        "c_type": c.c_type,
        "is_basic_list": False,
        "items": items,
        "year": 0,
        "month": 0,
        "category_items": _get_category_items(c.c_type),
    }
    return render_template('list_trade.html', **context)


@login_required
@update_basic_context
def analytics_trade_by_year(c_type):
    year = int(request.args.get('year', '0'))
    if year == 0:
        year = date.today().year

    q = TradeItem.query_by_c_type(str2category(c_type))
    q = q.filter(TradeItem.date >= date(year, 1, 1))
    q = q.filter(TradeItem.date <= date(year, 12, 31))
    q = q.order(TradeItem.date, TradeItem.description)

    #categorys = _get_category_items(c_type)
    items = [d for d in q.fetch()]
    context = {
        "c_type": c_type,
        "items": items,
        "year": year,
        "category_items": _get_category_items(c_type),
    }
    return render_template('analytics_trade_by_year.html', **context)


@login_required
@update_basic_context
def edit_trade(url_key):
    item = ndb.Key(urlsafe=url_key).get()
    assert isinstance(item, TradeItem)

    if request.method == "GET":
        context = {
            "item": item,
            "c_type": category2str(item.c_type),
            "category_items": _get_category_items(item.c_type),
        }
        return render_template('edit_trade.html', **context)

    else:  # POST => update
        category_key = request.form['category']
        item.category_key = ndb.Key(urlsafe=category_key)
        item.price = float(request.form['price'])
        item.description = request.form['description']
        item.date = str2date(request.form['date'])
        item.put_update_index()
        item.refresh()

        return redirect('/list/trade/%s?year=%s&month=%s' % (category2str(item.c_type), item.date.year, item.date.month))


@login_required
@update_basic_context
def add_trade(c_type):
    if request.method == "GET":
        context = {
            'today': date.today(),
            "c_type": c_type,
            "category_items": [d for d in TradeCategory.query_by_c_type(str2category(c_type)).fetch()],
        }
        return render_template('add_trade.html', **context)

    else:
        category_key_urlsafe = request.form['category']
        category_key = ndb.Key(urlsafe=category_key_urlsafe)

        t = TradeItem(
            user=users.get_current_user(),
            category_key=category_key,
            c_type=category_key.get().c_type,
            description=request.form['description'],
            price=int(request.form['price']),
            date=str2date(request.form['date']),
        )
        t.put_update_index(create=True)
        return redirect(url_for('index'))


@login_required
@update_basic_context
def remove_trade(url_key):
    year = int(request.args.get('year', '0'))
    month = int(request.args.get('month', '0'))

    item = ndb.Key(urlsafe=url_key).get()
    assert isinstance(item, TradeItem)
    item.delete()
    item.refresh()

    if year and month:
        return redirect('/list/trade/%s?year=%s&month=%s' % (category2str(item.c_type), year, month))
    else:
        return redirect('/list/trade/'+category2str(item.c_type))


# ========================================== TradeCategory ==========================================

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
            "category_items": _get_category_items(item.c_type),
        }
        return render_template('edit_category.html', **context)

    else:  # POST => update
        parent_category = request.form['parent_category']
        if parent_category:
            parent_category = ndb.Key(urlsafe=parent_category).get()

        item.description = request.form['description']
        item.parent_key = parent_category.key if parent_category else None
        item.put()
        item.refresh()

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


# ========================================== Search ==========================================

def search_text():
    text = request.args.get('text')

    index = search.Index(name=TradeItem.SEARCH_INDEX_KEY)
    results = index.search('description:'+text)

    items = []
    for doc in results:
        item = ndb.Key(urlsafe=doc.doc_id).get()
        items.append(item)
    items = sorted(items, key=lambda x: x.date, reverse=True)

    # treat all search result as CATEGORY_OUT now
    # may cause mistake, but just work on it
    c_type = CATEGORY_OUT
    context = {
        "c_type": category2str(c_type),
        "is_basic_list": False,
        "items": items,
        "category_items": _get_category_items(c_type),
    }
    return render_template('list_trade.html', **context)


# ========================================== Ajax ==========================================

def ajax_hello():
    obj = request.get_json()
    return jsonify(result=obj['msg'])


# ========================================== API ==========================================

@login_required
def api_category():
    out_items = []
    q = TradeCategory.query_by_c_type(CATEGORY_OUT)
    for d in q.fetch():
        out_items.append(d.to_json())
    in_items = []
    q = TradeCategory.query_by_c_type(CATEGORY_IN)
    for d in q.fetch():
        in_items.append(d.to_json())

    context = {
        category2str(CATEGORY_IN): in_items,
        category2str(CATEGORY_OUT): out_items,
    }
    return jsonify(**context)

@login_required
def api_add_trade():
    """
       category will follow by the category_key(maybe CATEGORY_IN or CATEGORY_OUT)
    """
    items = request.get_json()
    for item in items:
        category_key = ndb.Key(urlsafe=item['category'])

        t = TradeItem(
            user=users.get_current_user(),
            category_key=category_key,
            c_type=category_key.get().c_type,
            description=item['description'],
            price=int(item['price']),
            date=str2date(item['date']),
        )
        t.put_update_index(create=True)
        t.refresh()

    context = {
        'result': True,
    }
    return jsonify(**context)


