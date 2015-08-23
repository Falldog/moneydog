<script type="text/javascript">
'use strip'

angular.module('moneydogApp')
.controller('Controller', function() {
  var vm = this;

  vm.category = [
    {% for c in category_items %}
        {'key': '{{c.key.id()}}',
         'parent_key': '{% if c.parent_key %}{{c.parent_key.id()}}{% endif %}',
         'desc': {{c.description|tojson}},
         'count': 0,
        },
    {% endfor %}
  ];

  vm.trade_items = [
    {% for item in items %}
        {'key': '{{item.key.id()}}',
         'key_urlsafe': '{{item.key.urlsafe()}}',
         'category_key': '{{item.category_key.id()}}',
         'price': {{item.price}},
         'date': '{{item.date}}',
         'desc': {{item.description|tojson}},
        },
    {% endfor %}
  ];

  vm.analytics_trade = {};
  function analytics(cur_page, trade_items){
    for(var i=0 ; i<trade_items.length ; ++i){
        vm.analytics_trade[cur_page]
    }
  }

  vm.count_by_category = function(category) {
    category_key = category.key;
    var count = 0;
    var trade_items = vm.trade_items;
    for(var i=0 ; i<trade_items.length ; ++i){
        if(trade_items[i].category_key == category_key)
            count += trade_items[i].price;
    }
    return count;
  };
  for(var i=0 ; i < vm.category.length ; i++){
    var count = vm.count_by_category(vm.category[i]);
    vm.category[i]['count'] = count;
  }

});

</script>
