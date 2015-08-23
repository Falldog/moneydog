<script type="text/javascript">
'use strip'

angular.module('moneydogApp')
.controller('Controller', ['$scope', '$sce', function ($scope, $sce) {

  $scope.category = [
    {% for c in category_items %}
        {'key': '{{c.key.id()}}',
         'parent_key': '{% if c.parent_key %}{{c.parent_key.id()}}{% endif %}',
         'desc': {{c.description|tojson}},
         'count': 0,
        },
    {% endfor %}
  ];

  $scope.trade_items = [
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

  $scope.analytics_trade = {};
  function analytics(cur_page, trade_items){
    for(var i=0 ; i<trade_items.length ; ++i){
        $scope.analytics_trade[cur_page]
    }
  }

  $scope.count_by_category = function(category) {
    category_key = category.key;
    var count = 0;
    var trade_items = $scope.trade_items;
    for(var i=0 ; i<trade_items.length ; ++i){
        if(trade_items[i].category_key == category_key)
            count += trade_items[i].price;
    }
    return count;
  };
  for(var i=0 ; i < $scope.category.length ; i++){
    var count = $scope.count_by_category($scope.category[i]);
    $scope.category[i]['count'] = count;
  }

}]);

// for testing
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

</script>
