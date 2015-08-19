'use strict'

function CategoryService($q, $http){
  var self = this;
  var deferred = $q.defer();
  $http.get('/api/category')
    .then(function(response){
      console.log(response.data);
      deferred.resolve(response.data);
    },function(errResponse){
      console.log('error');
    });

  this.get = function(){
    return deferred.promise;
  };
}

angular.module('moneydogApp')
  .service('CategoryService', ['$q', '$http', CategoryService]);


