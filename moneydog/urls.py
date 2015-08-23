from moneydog import app
from moneydog import views
from moneydog import views_admin


app.add_url_rule('/', 'index', views.index)
#app.add_url_rule('/login', 'login', views.login)
app.add_url_rule('/list/trade/<c_type>', 'list_trade', views.list_trade)
app.add_url_rule('/list/trade/by_category/<url_key>', 'list_trade_by_category', views.list_trade_by_category)
app.add_url_rule('/edit/trade/<url_key>', 'edit_trade', views.edit_trade, methods=['GET', 'POST'])
app.add_url_rule('/add/trade/<c_type>', 'add_trade', views.add_trade, methods=['GET', 'POST'])
app.add_url_rule('/remove/trade/<url_key>', 'remove_trade', views.remove_trade)
app.add_url_rule('/list/category/<c_type>', 'list_category', views.list_category)
app.add_url_rule('/edit/category/<url_key>', 'edit_category', views.edit_category, methods=['GET', 'POST'])
app.add_url_rule('/remove/category/<url_key>', 'remove_category', views.remove_category)
app.add_url_rule('/add/category', 'add_category', views.add_category, methods=['GET', 'POST'])

app.add_url_rule('/analytics/trade/year/<c_type>', 'analytics_trade_by_year', views.analytics_trade_by_year)
app.add_url_rule('/search/', 'search_text', views.search_text)

app.add_url_rule('/ajax/hello', 'ajax_hello', views.ajax_hello, methods=['POST'])
app.add_url_rule('/api/category', 'api_category', views.api_category, methods=['GET', 'POST'])
app.add_url_rule('/api/add/trade', 'api_add_trade', views.api_add_trade, methods=['POST'])


# admin control view
app.add_url_rule('/admin/dump', 'dump', views_admin.dump)
app.add_url_rule('/admin/push_ancient_data', 'push_ancient_data', views_admin.push_ancient_data, methods=['GET', 'POST'])

