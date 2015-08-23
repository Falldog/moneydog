<script type="text/javascript">
'use strip'

angular.module('moneydogApp')
  .controller('Controller', [ '$http', function($http) {
    var vm = this;
    vm.items = [];
    vm.type = '{{c_type}}';
    vm.category = [
      {% for c in category_items %}
        {'key': '{{c.key.urlsafe()}}',
         'parent_key': '{% if c.parent_key %} {{c.parent_key.urlsafe()}} {% endif %}',
         'description': {{c.description|tojson}},
        },
      {% endfor -%}
    ];

    vm.add = function(){
      var today = '{{today}}';
      var date = vm.items.length ? vm.items[vm.items.length-1].date : today;
      if(vm.items.length)
        console.log(vm.items[vm.items.length-1].date);

      vm.items.push({
        'category': vm.category[0].key,
        'date': date,
        'description': '',
        'price': 0,
      });
    }; // add

    vm.submit = function(){
      console.log(vm.items);
      for(var i=0 ; i<vm.items.length ; i++){
        var item = vm.items[i];
        if( (!item.price || parseInt(item.price)<=0) ||
            !item.date ){
          alert('format error!');
          return false;
        }
      }

      $http.post('/api/add/trade', vm.items)
        .then(function(response){
           var result = response.data;
           if(result){
             location.href = '/list/trade/'+vm.type;
           }
        }, function(errResponse){
           console.log('error');
        });

    }; // submit

    vm.add(); // add first item

  }]);

</script>
