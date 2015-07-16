from moneydog import app
from moneydog.models import str2category, category2str

from datetime import date


app.jinja_env.filters['str2category'] = str2category
app.jinja_env.filters['category2str'] = category2str

@app.template_filter('reverse')
def reverse_filter(s):
    return s[::-1]

@app.template_filter('format_date')
def format_date(obj):
    if obj and isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    return None

