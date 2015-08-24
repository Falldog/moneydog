<script type="text/javascript">
'use strip'

angular.module('moneydogApp')
  .controller('Controller', [function() {
    var vm = this;
    vm.date = '{{item.date|format_date}}';

    vm.submit = function(){
      startSpinner();
    }
  }]);

</script>
