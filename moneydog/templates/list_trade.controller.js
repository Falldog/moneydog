<script type="text/javascript">
'use strip'

angular.module('moneydogApp')
.controller('Controller', ['$sce', function ($sce) {
  var vm = this;
  vm.predicate = 'date';
  vm.reverse = false;

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
         'desc': $sce.trustAsHtml({{item.description|tojson|safe}}),  // include html tag for ng-bind-html
        },
    {% endfor %}
  ];

  vm.total = 0;
  vm.max_item = vm.trade_items[0];
  for(var i=0 ; i < vm.trade_items.length ; i++){
    var item = vm.trade_items[i];
    vm.total += item.price;
    if(item.price > vm.max_item.price)
      vm.max_item = item;
  }

  vm.order = function(predicate){
    vm.reverse = (vm.predicate == predicate) ? !vm.reverse : false;
    vm.predicate = predicate;
  }

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

}]);

// for testing
/*
angular.module('moneydogApp')
  .run( function($http){
    // Simple POST request example (passing data) :
    $http.post('/ajax/hello', {msg:'hello word!!!'}).
      then(function(response){
        console.log('fuck success : '+response.data.result);
      },
      function(errResponse){
        console.log('fuck error');
      });
  });
*/

</script>
