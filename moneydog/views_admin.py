from flask import request
from flask import render_template
from flask import abort, redirect, url_for

from google.appengine.api import users
from google.appengine.ext import ndb

from moneydog import app
from moneydog.models import TradeCategory, TradeItem, CATEGORY_IN, CATEGORY_OUT, str2category
from moneydog.lib.decorators import login_required, update_basic_context
from google.appengine.ext.ndb import model

import json
import time
from datetime import date


@login_required
@update_basic_context
def dump():
    context = {
        "category_in_count": TradeCategory.query().filter(TradeCategory.c_type==CATEGORY_IN).count(),
        "category_out_count": TradeCategory.query().filter(TradeCategory.c_type==CATEGORY_OUT).count(),
        "in_count": TradeItem.query().filter(TradeItem.c_type==CATEGORY_IN).count(),
        "out_count": TradeItem.query().filter(TradeItem.c_type==CATEGORY_OUT).count(),
    }
    return render_template('admin/dump.html', **context)


@login_required
@update_basic_context
def push_ancient_data():
    if request.method == 'GET':
        return render_template('admin/push_ancient_data.html')

    else:
        _time = time.time()
        jdata = request.form['data'].strip()
        data = json.loads(jdata)
        c_map_in = {}
        c_map_out = {}
        user = users.get_current_user()
        for d in data['category_in']:
            t = TradeCategory(user=user, c_type=CATEGORY_IN, description=d['description'])
            c_map_in[t.description] = t
        ndb.put_multi(c_map_in.values())

        for d in data['category_out']:
            t = TradeCategory(user=user, c_type=CATEGORY_OUT, description=d['description'])
            c_map_out[t.description] = t
        ndb.put_multi(c_map_out.values())

        items_out = []
        for d in data['out']:
            tm = time.strptime(d['dt'], '%Y-%m-%d')
            dt = date(year=tm.tm_year, month=tm.tm_mon, day=tm.tm_mday)
            t = TradeItem(user=user, c_type=CATEGORY_OUT,
                          price=d['pr'], description=d['ds'], category_key=c_map_out[d['ct']].key, date=dt)
            items_out.append(t)

        ndb.put_multi(items_out)

        items_in = []
        for d in data['in']:
            tm = time.strptime(d['dt'], '%Y-%m-%d')
            dt = date(year=tm.tm_year, month=tm.tm_mon, day=tm.tm_mday)
            t = TradeItem(user=user, c_type=CATEGORY_IN,
                          price=d['pr'], description=d['ds'], category_key=c_map_in[d['ct']].key, date=dt)
            items_in.append(t)

        ndb.put_multi(items_in)

        for i in items_out:
            i.create_search_index()
        for i in items_in:
            i.create_search_index()

        context = {
            'done': True,
            'in_count': len(data['in']),
            'out_count': len(data['out']),
            'category_in_count': len(data['category_in']),
            'category_out_count': len(data['category_out']),
            'spend_time': time.time() - _time,
        }
        return render_template('admin/push_ancient_data.html', **context)
